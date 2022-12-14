#! /usr/bin/python

from syslog import syslog
from sys import argv
from scapy.all import sniff,conf,DNS,IP,IPv6,UDP
from wakeonlan import send_magic_packet

if len(argv) != 6:
    raise ValueError('Please provide listen_interface, listen_ip, listen_dns, host_ip and host_mac to send magic packages.')

listen_interface   = argv[1]
listen_ip   = argv[2]
listen_dns = argv[3].encode('utf-8')
host_ip  = argv[4]
host_mac = argv[5]


def handler(req):
    dns = req.getlayer(DNS)
    if dns.qr == 0 and dns.qd.qname == listen_dns:
        send_magic_packet(host_mac,ip_address=host_ip)
        syslog(f"Received DNS query for {listen_dns} and send magic package to IP: {host_ip} MAC: {host_mac}")

if __name__ == '__main__':

    syslog(f'Start watching for DNS Query {listen_dns} on Interface {listen_interface} IP {listen_ip} and wake up IP {host_ip} MAC {host_mac} if DNS Query occurs.')
    
    conf.sniff_promisc = False
    conf.layers.filter([IP, IPv6, UDP, DNS])

    sniff(iface=f"{listen_interface}",filter=f"ip dst {listen_ip} and udp and port 53", lfilter=lambda x: x.haslayer(DNS), prn=handler, store=0)