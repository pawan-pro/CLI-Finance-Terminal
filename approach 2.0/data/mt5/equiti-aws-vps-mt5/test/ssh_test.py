#!/usr/bin/env python3
"""
SSH Connection Test for MT5 Data Retrieval

This script tests SSH connectivity to the AWS instance and retrieves MT5 data CSVs.
"""

import os
import sys
import paramiko
import socket
from pathlib import Path
import subprocess

# Configuration
INSTANCE_HOST = "13.40.182.210"  # From details.txt
INSTANCE_USERNAME = "Administrator"
INSTANCE_KEY_PATH = "/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/mt5/equiti-aws-vps-mt5/VPS-MT5.pem"  # Relative to this script location
INSTANCE_DATA_DIR = "C:\\Users\\Administrator\\AppData\\Roaming\\MetaQuotes\\Terminal\\DD0DD2E2D928BE723A6D245A160D3117\\MQL5\\Files"

def setup_ssh_key_permissions(key_path):
    """Ensure SSH private key has correct permissions"""
    os.chmod(key_path, 0o600)

def test_ssh_connection():
    """Test SSH connection to the AWS instance"""
    try:
        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(INSTANCE_KEY_PATH)
        
        # Create SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Attempting to connect to {INSTANCE_HOST}...")
        
        # Connect to the instance
        ssh_client.connect(
            hostname=INSTANCE_HOST,
            username=INSTANCE_USERNAME,
            pkey=private_key,
            timeout=10
        )
        
        print("Successfully connected to the instance!")
        
        # Test command to check if system is responsive
        stdin, stdout, stderr = ssh_client.exec_command("echo 'Connection test successful'")
        response = stdout.read().decode().strip()
        print(f"Response from server: {response}")
        
        return ssh_client
        
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your key file and username.")
        return None
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
        return None
    except socket.timeout:
        print("Connection timed out. Please check if the server is running and accessible.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def list_csv_files(ssh_client):
    """List CSV files on the instance"""
    try:
        print(f"\nLooking for CSV files in: {INSTANCE_DATA_DIR}")
        
        # Command to list CSV files using PowerShell
        # Get just the names of CSV files
        command = f'powershell "Get-ChildItem -Path \'{INSTANCE_DATA_DIR}\' -Name -Include \'*.csv\'"'
        
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if output:
            print("CSV files found:")
            csv_files = [line.strip() for line in output.strip().split('\n') if line.strip() and '.csv' in line.lower()]
            for file in csv_files:
                print(f"  - {file}")
            return csv_files
        else:
            print("No CSV files found or error occurred.")
            if error:
                print(f"Error output: {error}")
            # Try alternative command in case powershell isn't accessible
            command = f'cmd /c "dir "{INSTANCE_DATA_DIR}" *.csv /b"'
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode()
            if output:
                print("Alternative command found these files:")
                csv_files = [line.strip() for line in output.strip().split('\n') if line.strip()]
                for file in csv_files:
                    print(f"  - {file}")
                return csv_files
            return []
            
    except Exception as e:
        print(f"Error listing CSV files: {e}")
        return []

def retrieve_csv_files(ssh_client, remote_csv_files, local_dir):
    """Retrieve CSV files from the remote instance"""
    try:
        sftp = ssh_client.open_sftp()
        
        # Create local directory if it doesn't exist
        Path(local_dir).mkdir(exist_ok=True)
        
        print(f"\nRetrieving CSV files to: {local_dir}")
        
        for remote_file in remote_csv_files:
            # Windows uses backslashes, but SFTP might expect forward slashes
            remote_path = f"{INSTANCE_DATA_DIR}\\{remote_file}".replace("\\", "/")
            local_path = os.path.join(local_dir, remote_file)
            
            print(f"Downloading {remote_file}...")
            
            try:
                sftp.get(remote_path.replace("\\", "/"), local_path)
                print(f"Successfully downloaded {remote_file}")
            except Exception as e:
                print(f"Failed to download {remote_file} from path {remote_path.replace(chr(92), '/')}: {e}")
        
        sftp.close()
        print(f"\nAll files downloaded to {local_dir}")
        
    except Exception as e:
        print(f"Error retrieving files: {e}")

def main():
    print("MT5 Data Retrieval via SSH - Test Script")
    print("=" * 50)
    
    # Check if the key file exists
    key_path = os.path.join(os.path.dirname(__file__), INSTANCE_KEY_PATH)
    if not os.path.exists(key_path):
        print(f"Error: Key file not found at {key_path}")
        return
    
    # Set proper permissions on SSH key (Linux/Mac only)
    if os.name != 'nt':  # Not Windows
        setup_ssh_key_permissions(key_path)
    
    # Test SSH connection
    ssh_client = test_ssh_connection()
    
    if ssh_client is None:
        print("Failed to establish SSH connection. Exiting.")
        return
    
    try:
        # List CSV files
        csv_files = list_csv_files(ssh_client)
        
        if csv_files:
            print(f"\nFound {len(csv_files)} CSV files")
            
            # Create a directory for retrieved files
            local_download_dir = os.path.join(os.path.dirname(__file__), "retrieved_data")
            
            # Retrieve the CSV files
            retrieve_csv_files(ssh_client, csv_files, local_download_dir)
        else:
            print("No CSV files found on the remote instance.")
    
    finally:
        # Close the SSH connection
        ssh_client.close()
        print("\nSSH connection closed.")

if __name__ == "__main__":
    main()