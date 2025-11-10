#!/usr/bin/env python3
"""
Comprehensive Test Script for MT5 Data Retrieval

This script provides multiple approaches for connecting to the Windows AWS instance
to retrieve MT5 data CSVs. It includes methods for both SSH and WinRM connections.
"""

import os
import sys
from pathlib import Path
import subprocess
import socket

def check_port(host, port):
    """Check if a port is open on the host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("Comprehensive MT5 Data Retrieval Test")
    print("=" * 50)
    
    host = "13.40.182.210"
    print(f"Testing connectivity to: {host}")
    
    # Check available ports
    ports = {
        22: "SSH",
        135: "RPC Endpoint Mapper (WinRM)", 
        139: "NetBIOS Session Service",
        443: "HTTPS",
        445: "SMB",
        593: "HTTP RPC Endpoint Mapper",
        3389: "RDP",
        5985: "WinRM HTTP",
        5986: "WinRM HTTPS"
    }
    
    print("\nPort connectivity test results:")
    open_ports = []
    for port, service in ports.items():
        is_open = check_port(host, port)
        status = "OPEN" if is_open else "CLOSED"
        print(f"  {port:>5} ({service:<20}): {status}")
        if is_open:
            open_ports.append(port)
    
    print(f"\nOpen ports: {open_ports}")
    
    print("\n" + "="*50)
    print("CONNECTION OPTIONS:")
    print("="*50)
    
    # Option 1: Direct RDP access
    if 3389 in open_ports:
        print("✓ RDP Access Available (Port 3389)")
        print("  - Connect via: mstsc /v:13.40.182.210")
        print("  - Username: Administrator")
        print("  - Use AWS Console to get password from VPS-MT5.pem")
        print("  - You can manually copy files via RDP once connected\n")
    
    # Option 2: SSH (if available)
    if 22 in open_ports:
        print("✓ SSH Access Available (Port 22)")
        print("  - Use ssh_test.py script with your private key\n")
    else:
        print("✗ SSH Access Not Available (Port 22)")
        print("  - SSH is not enabled on the Windows instance by default")
        print("  - You need to install and configure OpenSSH Server on the Windows instance\n")
    
    # Option 3: WinRM (if available)
    winrm_available = 5985 in open_ports or 5986 in open_ports
    if winrm_available:
        winrm_ports = [p for p in [5985, 5986] if p in open_ports]
        print(f"✓ WinRM Access Available (Port {', '.join(map(str, winrm_ports))})")
        print("  - Use winrm_test.py script after installing required libraries\n")
    else:
        print("✗ WinRM Access Not Available (Ports 5985, 5986)")
        print("  - WinRM is not enabled on the Windows instance by default")
        print("  - You need to enable PowerShell Remoting on the Windows instance via RDP\n")
    
    print("="*50)
    print("RECOMMENDED SETUP PROCESS:")
    print("="*50)
    print("1. Connect to the instance via RDP (port 3389)")
    print("2. Configure the Windows instance to enable remote access:")
    print("   For SSH: Install OpenSSH Server and configure")
    print("   For WinRM: Enable-PSRemoting -Force and configure firewall")
    print("3. Test the remote access method of your choice")
    print("4. Retrieve your MT5 CSV data")
    
    print("\n" + "="*50)
    print("FILES LOCATION ON WINDOWS INSTANCE:")
    print("C:\\Users\\Administrator\\AppData\\Roaming\\MetaQuotes\\Terminal\\DD0DD2ED928BE723A6D245A160D3117\\MQL5\\Files")
    print("="*50)

if __name__ == "__main__":
    main()