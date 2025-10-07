
set_a_cookie = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unauthorized (403)</title>
    <script>
        function setAuthCookie() {
            var authValue = document.getElementById("authTextbox").value;
            if (authValue) {
                var expiresDate = new Date();
                expiresDate.setFullYear(expiresDate.getFullYear() + 10);  // 10 years from now
                document.cookie = "auth=" + authValue + "; expires=" + expiresDate.toUTCString() + "; path=/";
                window.location.reload();
            } else {
                alert("Please enter a value");
            }
        }
    </script>
</head>
<body>

    <h2>Unauthorized (403)</h2>
    
    <input type="text" id="authTextbox" placeholder="Enter auth value">
    <button onclick="setAuthCookie()">Auth</button>

</body>
</html>
"""

