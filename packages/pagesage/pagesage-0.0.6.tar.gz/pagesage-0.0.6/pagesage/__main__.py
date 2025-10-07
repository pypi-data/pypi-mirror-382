"""
pagesage main module.
"""
from flask import Flask, render_template_string, send_from_directory, abort, Response, send_file, request
from markdown import markdown
from pagesage.auth import set_a_cookie
from pagesage.template import assemble
import click
import logging
import os
import pagesage as app
import sys
import textwrap

logging.basicConfig()
logger = logging.getLogger("pagesage")
logger.setLevel(logging.WARNING)
web = Flask(__name__)
website = None

def trim_path(p):
    '''Return path p without trailing slashes "/".'''
    while p.endswith("/"):
        p = p[:-1]
    return p

def is_above_curdir(path):
    '''Return true if the path is above current (doc root) directory.'''
    # Get the absolute paths
    if path == "/":
        return False
    curdir = os.path.abspath(os.getcwd())
    abspath = os.path.abspath(path)
    # Check if the target path is above the current directory
    return os.path.commonpath([curdir]) != os.path.commonpath([curdir, abspath])

def from_local_root(path):
    '''Return path prepended with curdir (doc root).'''
    # Needed for flask because it ignores current directory
    curdir = os.getcwd()
    return os.path.join(curdir, path)

def location_header(url):
    '''Return html of a current url path with links on each dir.'''
    logger.debug(f"Location header processing url: {url}")
    header = '[🏠](/)/'
    if url == '.':
        return md_to_html(trim_path(header)+"  \n\n")
    links = url.split("/")
    for i in range(0, len(links)):
        header += f'[{links[i]}](/{"/".join(links[:i+1])})/'
    return md_to_html(trim_path(header)+"  \n\n")

def list_dir(url):
    '''Return html with directory listing. Used for url that is a directory and not a file.'''
    path = from_local_root(url)
    logger.debug(f"Listing path: {path} as url: {url}")
    # Iterate over the first level of contents in the directory
    md_item_list = ''
    for item in sorted(os.listdir(path)):
        if item.startswith("."):
            logger.debug(f"-- {item} is hidden.")
            continue
        item_path = os.path.join(path, item)
        item_url = os.path.join("/", url, item)
        if item_url.lower().endswith(".md"):
            logger.debug(f"-- {item} is a markdown file.")
            md_item_list += f'- [{item[:-3]}]({item_url[:-3]}) [📝]({item_url})\n'
        elif os.path.isdir(item_path):
            logger.debug(f"-- {item} is a directory.")
            md_item_list += f'- [📁 {item}]({item_url}/)\n'
        else:
            logger.debug(f"-- {item} is a file.")
            md_item_list += f'- [{item}]({item_url})\n'
    return markdown(md_item_list)

def md_to_html(md_data, prepend="", append=""):
    '''Parse md_file and return html. Add markdown contents from prepend and append before parsing.'''
    content = prepend + md_data + append
    html = markdown(
        content,
        extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.codehilite',
        'markdown.extensions.footnotes',
        'markdown.extensions.toc',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        #'markdown.extensions.codehilite(guess_lang=False)',
        ])
    return html

def file_to_html(md_file, prepend="", append=""):
    '''Parse md_file and return html. Add markdown contents from prepend and append before parsing.'''
    with open(md_file, 'r', encoding='utf-8') as f:
        return md_to_html(f.read(), prepend, append)


class Page():
    '''Object with html and mtime used to cache html rather than parse md each time.'''
    def __init__(self, mtime, html):
        self.mtime = mtime
        self.html = html


class Website():

    def __init__(self, auth):
        self.urls = dict()
        self.auth = auth

    def get(self, url):
        logger.debug(f"Getting url {url}")
        if is_above_curdir(url):
            logger.warn(f"{url} path above web root")
            return None
        header = location_header(url)
        if os.path.isdir(url):
            logger.debug(f"-- {url} is a directory")
            index_file = os.path.join(trim_path(url),'index.md')
            if os.path.exists(index_file):
                logger.debug(f"-- Found index.md in {url}. Attempting to serve.")
                content = file_to_html(index_file)
                html = assemble(content=content, header=header)
                return html
            logger.debug(f"-- Attempting to list {url}")
            content = list_dir(url)
            html = assemble(content=content, header=header)
            return html
        md_file = trim_path(url) + '.md'
        if not os.path.exists(md_file):
            logger.debug(f"-- {url} is not an md file.")
            if url in self.urls:
                logger.debug(f"-- {url} will be released from cache")
                del self.urls[url]
            return None
        mtime = os.path.getmtime(md_file)
        if url not in self.urls or mtime > self.urls[url].mtime:
            logger.debug(f"-- {url} has changed from last time. Updating.")
            content = file_to_html(md_file)
            html = assemble(content=content, header=header)
            self.urls[url] = Page(mtime, html)
        return self.urls[url].html


@web.route('/', methods=['GET'])
def serve_root():
    return serve_markdown(".")

@web.route('/<path:filepath>', methods=['GET'])
def serve_markdown(filepath):
    if website.auth:
        auth = request.cookies.get('auth')
        if auth != website.auth:
            logger.warn(f"Passwords do not match.")
            return set_a_cookie, 403
    content = website.get(filepath)
    if content:
        return content
    # Check if the markdown file exists
    logger.debug(f"{filepath} could not be found in the website. I'll attempt to serve it as a file.")
    if is_above_curdir(filepath):
        logger.warn(f"{filepath} path above web root")
        abort(404)
    if not os.path.exists(filepath):
        logger.warn(f"{filepath} file does not exist")
        abort(404)
    return send_file(from_local_root(filepath))


@click.group()
@click.version_option(
    version=app.__version__, message=f"%(prog)s %(version)s - {app.__copyright__}"
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Enable debug mode with output of each action in the log.",
)
@click.pass_context
def cli(ctx, **kwargs):
    if ctx.params.get("debug"):
        logger.setLevel(logging.DEBUG)
        logger.info("debug mode is on")


@cli.command()
@click.argument("port", default=8080)
@click.option("-a", "--auth", type=str, required=False, default=None)
def run(port, auth):
    "Serve current directory as web root."
    global website
    website = Website(auth)
    web.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    cli()

