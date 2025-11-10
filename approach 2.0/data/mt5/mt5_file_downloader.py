import paramiko
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# Configuration
REMOTE_HOST = "ec2-13-40-182-210.eu-west-2.compute.amazonaws.com"
REMOTE_USER = "Administrator"
REMOTE_PATH = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\DD0DD2ED928BE723A6D245A160D3117\MQL5\Files"
LOCAL_PATH = "/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/mt5/"
PEM_KEY_PATH = "/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/mt5/equiti-aws-vps-mt5/VPS-MT5.pem"

# Get password from environment variable (fallback to prompt)
PASSWORD = os.getenv('MT5_SSH_PASSWORD')

def download_csv_file(date_str=None):
    """
    Download CSV file from remote MT5 server
    
    Args:
        date_str: Date string in format YYYYMMDD (e.g., '20251023')
                 If None, uses today's date
    """
    # Generate filename
    if date_str is None:
        date_str = datetime.now().strftime('%Y%m%d')
    
    filename = f"{date_str}.csv"
    remote_file = f"{REMOTE_PATH}\\{filename}"
    local_file = os.path.join(LOCAL_PATH, filename)
    
    print(f"Attempting to download: {filename}")
    print(f"Remote: {remote_file}")
    print(f"Local: {local_file}")
    
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Try with PEM key first
        print("\nTrying SSH key authentication...")
        try:
            private_key = paramiko.RSAKey.from_private_key_file(PEM_KEY_PATH)
            ssh.connect(
                hostname=REMOTE_HOST,
                username=REMOTE_USER,
                pkey=private_key,
                timeout=10
            )
            print("✓ Connected with SSH key")
        except Exception as key_error:
            print(f"SSH key failed: {key_error}")
            
            # Fallback to password
            if PASSWORD:
                print("\nTrying password authentication...")
                ssh.connect(
                    hostname=REMOTE_HOST,
                    username=REMOTE_USER,
                    password=PASSWORD,
                    timeout=10
                )
                print("✓ Connected with password")
            else:
                raise Exception("No password found in environment variable MT5_SSH_PASSWORD")
        
        # Open SFTP session
        sftp = ssh.open_sftp()
        
        # Download file
        print(f"\nDownloading {filename}...")
        sftp.get(remote_file, local_file)
        
        # Get file size
        file_size = os.path.getsize(local_file)
        print(f"✓ Successfully downloaded {filename}")
        print(f"  Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        print(f"  Saved to: {local_file}")
        
        sftp.close()
        return True
        
    except FileNotFoundError:
        print(f"✗ Error: File not found on remote server: {remote_file}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        ssh.close()

def list_remote_files():
    """List all CSV files in the remote directory"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect
        if PASSWORD:
            ssh.connect(hostname=REMOTE_HOST, username=REMOTE_USER, password=PASSWORD)
        else:
            private_key = paramiko.RSAKey.from_private_key_file(PEM_KEY_PATH)
            ssh.connect(hostname=REMOTE_HOST, username=REMOTE_USER, pkey=private_key)
        
        sftp = ssh.open_sftp()
        
        # List files
        print(f"\nFiles in remote directory:")
        print("-" * 60)
        files = sftp.listdir(REMOTE_PATH)
        csv_files = [f for f in files if f.endswith('.csv')]
        
        for file in sorted(csv_files):
            file_path = f"{REMOTE_PATH}\\{file}"
            attrs = sftp.stat(file_path)
            size_mb = attrs.st_size / 1024 / 1024
            mod_time = datetime.fromtimestamp(attrs.st_mtime)
            print(f"{file:30} {size_mb:>8.2f} MB  {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        sftp.close()
        return csv_files
        
    except Exception as e:
        print(f"Error listing files: {e}")
        return []
    finally:
        ssh.close()

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("MT5 CSV File Downloader")
    print("=" * 60)
    
    # Check if date argument provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_remote_files()
        else:
            date_str = sys.argv[1]
            download_csv_file(date_str)
    else:
        # Download today's file by default
        download_csv_file()
    
    print("\n" + "=" * 60)