#!/usr/bin/env python3
"""
WinRM Connection Test for MT5 Data Retrieval

This script tests WinRM connectivity to the Windows AWS instance and retrieves MT5 data CSVs.
"""

import os
import sys
from pathlib import Path
import subprocess

def test_port_connectivity(host, port):
    """Test if a specific port is open on the host"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("MT5 Data Retrieval - Port Connectivity Test")
    print("=" * 50)
    
    host = "13.40.182.210"
    
    # Test common ports
    ports_to_test = [22, 3389, 5986]  # SSH, RDP, WinRM HTTPS
    port_names = {22: "SSH", 3389: "RDP", 5986: "WinRM HTTPS"}
    
    print(f"Testing connectivity to {host}...")
    
    for port in ports_to_test:
        is_open = test_port_connectivity(host, port)
        status = "OPEN" if is_open else "CLOSED"
        print(f"Port {port} ({port_names[port]}): {status}")
    
    print("\nBased on the connection details, this is a Windows machine accessible via RDP.")
    print("Standard SSH (port 22) is often not enabled by default on Windows instances.")
    print("You may need to enable PowerShell Remoting (WinRM) on the Windows instance first.")
    
    print("\nTo enable WinRM on the Windows instance, connect via RDP and run as Administrator:")
    print("  Enable-PSRemoting -Force")
    print("  Set-Item WSMan:\\localhost\\Client\\TrustedHosts -Value * -Force")
    print("  New-NetFirewallRule -Name \"WinRM-HTTPS-In\" -DisplayName \"WinRM-HTTPS-In\" -Protocol TCP -LocalPort 5986 -Action Allow -Profile Domain,Private,Public -Direction In")
    print("\nThen you can connect using WinRM from Python using the 'requests-credssp' or 'pypsrp' libraries.")

if __name__ == "__main__":
    main()