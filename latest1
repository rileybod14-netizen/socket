import socket
import sys
import os
import time
import http.client
from xml.sax.saxutils import escape


def c(text, color="white"):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "white": "\033[97m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, colors['white'])}{text}{colors['reset']}"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def discover_tvs(timeout=5):
    print(c(f"[*] Searching for LG devices ({timeout}s)...", "yellow"))

    msg = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: 239.255.255.250:1900\r\n"
        'MAN: "ssdp:discover"\r\n'
        "MX: 3\r\n"
        "ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n"
    )

    found = set()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        sock.sendto(msg.encode(), ("239.255.255.250", 1900))
        start = time.time()
        while time.time() - start < timeout:
            try:
                data, addr = sock.recvfrom(4096)
                text = data.decode(errors="ignore").upper()
                if "LG" in text or "WEBOS" in text or "NETCAST" in text:
                    found.add(addr[0])
            except socket.timeout:
                break
    finally:
        sock.close()

    return list(found)


def scan_ports(ip):
    ports = [8080, 3000, 3001]
    open_ports = []

    print(c(f"[*] Checking {ip}", "yellow"))

    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            if s.connect_ex((ip, port)) == 0:
                print(c(f"[+] {port}/TCP open", "green"))
                open_ports.append(port)
            else:
                print(c(f"[-] {port}/TCP closed", "red"))

    return open_ports


def udap_test(ip, port=8080):
    print(c("[*] Testing UDAP endpoint...", "yellow"))

    body = """<?xml version="1.0" encoding="utf-8"?>
<envelope>
 <api type="pairing">
  <name>LGTester</name>
 </api>
</envelope>
"""

    try:
        conn = http.client.HTTPConnection(ip, port, timeout=5)
        conn.request(
            "POST",
            "/udap/api/pairing",
            body,
            {"Content-Type": "application/xml"},
        )
        response = conn.getresponse()
        data = response.read().decode(errors="ignore")
        conn.close()
        print(c(data[:300], "blue"))
        return True
    except Exception as e:
        print(c(f"UDAP error: {e}", "red"))
        return False


def main():
    clear()
    print(c("LG TV Tester", "green"))

    devices = discover_tvs()

    if not devices:
        ip = input("Enter TV IP manually: ").strip()
    elif len(devices) == 1:
        ip = devices[0]
        print(c(f"Found: {ip}", "green"))
    else:
        for i, d in enumerate(devices, 1):
            print(f"{i}. {d}")
        ip = devices[int(input("Select: ")) - 1]

    ports = scan_ports(ip)

    if 8080 in ports:
        udap_test(ip)

    print(c("Done.", "green"))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExit")
        sys.exit(0)
