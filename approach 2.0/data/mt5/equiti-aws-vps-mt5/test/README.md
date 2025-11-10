# MT5 Data Retrieval Setup Guide

## Current Connection Status

The Windows AWS instance is currently accessible via:
- RDP (port 3389): ✅ Open
- SSH (port 22): ❌ Closed
- WinRM HTTPS (port 5986): ❌ Closed

## Steps to Enable WinRM Access

To retrieve MT5 data CSVs programmatically, you will need to enable WinRM on the Windows instance:

### 1. Connect via RDP
Use the provided RDP file to connect to the instance:
- Server: ec2-13-40-182-210.eu-west-2.compute.amazonaws.com
- Username: Administrator
- Use the VPS-MT5.pem file to get the password via AWS Console

### 2. Enable PowerShell Remoting on Windows Instance
Once connected as Administrator, open PowerShell as Administrator and run:

```powershell
# Enable PowerShell Remoting
Enable-PSRemoting -Force

# Configure WinRM for HTTPS
winrm quickconfig -transport:https

# Allow WinRM through firewall
New-NetFirewallRule -Name "WinRM-HTTPS-In" -DisplayName "WinRM-HTTPS-In" -Protocol TCP -LocalPort 5986 -Action Allow -Profile Domain,Private,Public -Direction In

# Configure trusted hosts (for testing - use more specific hosts in production)
Set-Item WSMan:\\localhost\\Client\\TrustedHosts -Value * -Force

# Create a self-signed certificate (if none exists)
$cert = New-SelfSignedCertificate -DnsName "localhost", "13.40.182.210" -CertStoreLocation "cert:\\LocalMachine\\My"
$thumbprint = $cert.Thumbprint

# Configure HTTPS listener with the certificate
winrm create "winrm/config/Listener?Address=*+Transport=HTTPS" "@{Port=`"5986`"; CertificateThumbprint=`"$thumbprint`"}"
```

## Alternative: SFTP/SSH Setup (if preferred)

If you prefer SSH access, you can install OpenSSH on the Windows instance:

1. Connect via RDP
2. Install OpenSSH Server:
   ```powershell
   # Install OpenSSH Server
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
   
   # Start and set SSH service to automatic
   Start-Service sshd
   Set-Service -Name sshd -StartupType 'Automatic'
   
   # Configure firewall rule
   if (!(Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue)) {
       New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
   }
   ```
3. Set up key-based authentication by placing your public key in:
   `C:\Users\Administrator\.ssh\authorized_keys`

## Python Code for WinRM Access

After enabling WinRM, you can use the following Python libraries:

```bash
pip install pypsrp
```

Example code to connect using WinRM:
```python
from pypsrp.client import Client

client = Client(
    "13.40.182.210", 
    username="Administrator", 
    password="your_password",  # Use appropriate authentication method
    ssl=True,
    port=5986,
    auth="basic"  # Or "ntlm", "kerberos", etc.
)

# Execute PowerShell commands
output, streams, had_errors = client.execute_ps('Get-ChildItem "C:\\Users\\Administrator\\AppData\\Roaming\\MetaQuotes\\Terminal\\DD0DD2ED928BE723A6D245A160D3117\\MQL5\\Files" -Filter "*.csv"')
print(output)
```

## Files Location
MT5 data files are located at:
`C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\DD0DD2ED928BE723A6D245A160D3117\MQL5\Files`

## Next Steps
1. Connect to the instance via RDP
2. Follow the steps above to enable WinRM or SSH
3. Test the connection using the scripts in this folder
4. Retrieve your MT5 data CSVs