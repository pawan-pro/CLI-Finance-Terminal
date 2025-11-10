# MT5 Data Retrieval via SSH/WinRM - Complete Solution

## Overview
This project provides tools and documentation for connecting to the AWS Windows instance and retrieving MT5 data CSV files. The test folder contains all necessary scripts and information.

## Files Included

### Scripts
- `ssh_test.py`: Tests SSH connection to the instance (may not work by default on Windows instances)
- `winrm_test.py`: Tests WinRM connection for Windows instances (requires WinRM setup)
- `port_test.py`: Tests connectivity to various ports on the instance
- `connection_test.py`: Comprehensive test of all possible connection methods
- `README.md`: Setup guide for enabling remote access

### Configuration
- `requirements.txt`: Required Python packages

## Current Findings
- Instance IP: 13.40.182.210
- Only RDP (port 3389) is accessible by default on the Windows instance
- SSH (port 22) and WinRM (ports 5985, 5986) are closed by default
- MT5 data location: `C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\DD0DD2ED928BE723A6D245A160D3117\MQL5\Files`

## Next Steps to Retrieve Data

### Option 1: RDP (Immediate Access)
1. Connect via RDP using the provided `.rdp` file or manually with:
   - Address: `13.40.182.210`
   - Username: `Administrator`
   - Password: Get from AWS Console using the VPS-MT5.pem file
2. Navigate to the MT5 data folder and manually copy files

### Option 2: Automated Access (Recommended for regular use)
1. Connect via RDP first
2. Enable WinRM or SSH on the Windows instance (see README.md)
3. Use the appropriate Python script to automate data retrieval

## Setup Commands for Windows Instance
Once connected via RDP as Administrator, run these PowerShell commands:

For WinRM access:
```powershell
Enable-PSRemoting -Force
Set-Item WSMan:\localhost\Client\TrustedHosts -Value * -Force
New-NetFirewallRule -Name "WinRM-HTTPS-In" -DisplayName "WinRM-HTTPS-In" -Protocol TCP -LocalPort 5986 -Action Allow -Profile Domain,Private,Public -Direction In
```

For SSH access:
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

## Python Libraries Used
- `paramiko`: For SSH connections
- `pypsrp`: For WinRM connections

## Security Notes
- The private key file (VPS-MT5.pem) contains sensitive information
- Store it securely and limit access
- When setting up remote access, consider using more secure configurations than those shown in examples