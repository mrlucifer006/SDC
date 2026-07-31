import subprocess
import re
import os
import time
import sys
import threading

def read_stream(stream, process_name):
    # This prevents the process from blocking if the OS buffer fills up
    for line in iter(stream.readline, ''):
        pass

def start_tunnel(port):
    print(f"Starting cloudflared tunnel on port {port}...")
    # Cloudflared logs to stderr
    cloudflared_exe = "cloudflared-windows-amd64.exe" if os.path.exists("cloudflared-windows-amd64.exe") else "cloudflared"
    
    process = subprocess.Popen(
        [cloudflared_exe, "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    url = None
    # We read from stderr because cloudflared prints the URL there
    for line in iter(process.stderr.readline, ''):
        # Look for the trycloudflare.com URL
        match = re.search(r'(https://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
        if match:
            url = match.group(1)
            break
            
    if not url:
        print(f"Failed to extract tunnel URL for port {port}.")
        process.kill()
        sys.exit(1)
        
    # Start a thread to consume the rest of stderr so it doesn't block
    threading.Thread(target=read_stream, args=(process.stderr, f"tunnel-{port}"), daemon=True).start()
    threading.Thread(target=read_stream, args=(process.stdout, f"tunnel-{port}"), daemon=True).start()
        
    return process, url

def main():
    cloudflared_exe = "cloudflared-windows-amd64.exe" if os.path.exists("cloudflared-windows-amd64.exe") else "cloudflared"
    
    try:
        # Check if cloudflared is installed
        subprocess.run([cloudflared_exe, "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print(f"Error: '{cloudflared_exe}' is not installed or not in your PATH.")
        print("Please download it from https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
        sys.exit(1)

    print("==========================================")
    print("🚀 Starting Backend Tunnel (Port 8000)...")
    backend_proc, backend_url = start_tunnel(8000)
    print(f"✅ Backend Tunnel URL: {backend_url}")
    print("==========================================\n")

    print("🐳 Building and starting Docker Compose services...")
    print("This may take a minute or two as it injects the new URL into the frontend build...")
    
    # Set the environment variable so docker-compose picks it up for the frontend build
    env = os.environ.copy()
    env["VITE_API_URL"] = backend_url
    
    # We must rebuild so Vite bakes the new API URL into the static frontend assets
    result = subprocess.run(["docker-compose", "up", "-d", "--build"], env=env)
    
    if result.returncode != 0:
        print("❌ Failed to start Docker Compose.")
        backend_proc.kill()
        sys.exit(1)
        
    print("✅ Docker Compose started successfully.\n")

    print("==========================================")
    print("🚀 Starting Frontend Tunnel (Port 5173)...")
    frontend_proc, frontend_url = start_tunnel(5173)
    print("==========================================\n")

    print("🎉 ALL SYSTEMS GO!")
    print(f"🔗 Share this link with your participants: {frontend_url}")
    print("\n⚠️ DO NOT CLOSE THIS WINDOW.")
    print("Press Ctrl+C to stop tunnels and docker containers.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping tunnels...")
        backend_proc.kill()
        frontend_proc.kill()
        print("🛑 Stopping docker containers (this might take a few seconds)...")
        subprocess.run(["docker-compose", "down"])
        print("✅ Shutdown complete.")

if __name__ == "__main__":
    main()
