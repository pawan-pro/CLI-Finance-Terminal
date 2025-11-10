#!/usr/bin/env python3
"""
WinRM-based MT5 Data Retrieval Script

This script connects to a Windows AWS instance using WinRM to retrieve MT5 data CSVs.
Note: Requires WinRM to be configured on the target Windows instance.

To prepare the Windows instance, follow the instructions in README.md
"""

import os
import sys
from pathlib import Path
import subprocess

def check_winrm_libraries():
    """Check if required WinRM libraries are available"""
    try:
        import requests
        import pypsrp
        return True
    except ImportError as e:
        print(f"Required library not found: {e}")
        print("Install with: pip install pypsrp")
        return False

def test_winrm_connection(host, username, password=None, cert_path=None):
    """Test WinRM connection - requires additional setup on Windows instance"""
    if not check_winrm_libraries():
        return False
    
    try:
        from pypsrp.client import Client
        
        # Try connecting with different authentication methods
        auth_methods = ['basic', 'ntlm', 'kerberos']
        
        for auth_method in auth_methods:
            try:
                print(f"Trying to connect with {auth_method} authentication...")
                
                client = Client(
                    host,
                    username=username,
                    # For security, use more appropriate authentication method
                    # This is just a basic example
                    password=password,
                    ssl=True,
                    port=5986,
                    auth=auth_method,
                    # For initial test, we'll skip cert verification
                    # In production, use proper certificate validation
                    cert_validation=False
                )
                
                # Test the connection
                output, streams, had_errors = client.execute_ps('echo "WinRM Connection Test Successful"')
                
                if output and not had_errors:
                    print(f"Successfully connected using {auth_method} authentication!")
                    print(f"Response: {output.strip()}")
                    return client
                else:
                    print(f"Connection test failed with {auth_method}: {streams}")
                    
            except Exception as e:
                print(f"Failed to connect with {auth_method}: {e}")
                continue
    
        print("Could not establish WinRM connection with any authentication method.")
        return None
        
    except Exception as e:
        print(f"Error establishing WinRM connection: {e}")
        return None

def list_mt5_csv_files_winrm(client):
    """List MT5 CSV files using WinRM connection"""
    try:
        # PowerShell command to list CSV files in the MT5 data directory
        ps_command = '''
        $dataPath = "C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\DD0DD2ED928BE723A6D245A160D3117\MQL5\Files"
        if (Test-Path $dataPath) {
            Get-ChildItem -Path $dataPath -Filter "*.csv" | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
        } else {
            Write-Output "Data directory does not exist: $dataPath"
        }
        '''
        
        print("Retrieving list of CSV files...")
        output, streams, had_errors = client.execute_ps(ps_command)
        
        if had_errors:
            print(f"Error executing command: {streams}")
            return []
        
        print("CSV files found:")
        print(output)
        
        # Parse the output to get just the filenames
        lines = output.strip().split('\n')
        csv_files = []
        for line in lines:
            # Look for lines that contain .csv files
            if '.csv' in line.lower():
                # Extract filename (assumes it's in the format we expect from Format-Table)
                parts = line.split()
                for part in parts:
                    if part.lower().endswith('.csv'):
                        csv_files.append(part.strip())
        
        # If parsing didn't work, try a simpler approach
        if not csv_files:
            ps_command_simple = 'Get-ChildItem -Path "C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\DD0DD2ED928BE723A6D245A160D3117\MQL5\Files" -Name -Include "*.csv"'
            output, streams, had_errors = client.execute_ps(ps_command_simple)
            if not had_errors and output:
                csv_files = [name.strip() for name in output.strip().split('\n') if name.strip()]
        
        return csv_files
        
    except Exception as e:
        print(f"Error listing CSV files: {e}")
        return []

def download_mt5_csv_files_winrm(client, csv_files, local_dir):
    """Download MT5 CSV files using WinRM + PowerShell file operations"""
    try:
        # Create local directory if it doesn't exist
        Path(local_dir).mkdir(exist_ok=True)
        
        print(f"Downloading {len(csv_files)} CSV files to: {local_dir}")
        
        # For each file, we'll use PowerShell to read the content and return it
        for csv_file in csv_files:
            print(f"Downloading {csv_file}...")
            
            # Read the file content via PowerShell and transfer
            ps_command = f'''
            $filePath = "C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\DD0DD2ED928BE723A6D245A160D3117\MQL5\Files\{csv_file}"
            if (Test-Path $filePath) {{
                Get-Content -Path $filePath -Raw
            }} else {{
                Write-Output "File does not exist: $filePath"
            }}
            '''
            
            try:
                output, streams, had_errors = client.execute_ps(ps_command)
                
                if had_errors:
                    print(f"Error downloading {csv_file}: {streams}")
                    continue
                
                # Write the content to a local file
                local_file_path = os.path.join(local_dir, csv_file)
                with open(local_file_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                
                print(f"Successfully downloaded {csv_file}")
                
            except Exception as e:
                print(f"Failed to download {csv_file}: {e}")
        
        print(f"\nAll files downloaded to {local_dir}")
        
    except Exception as e:
        print(f"Error downloading CSV files: {e}")

def main():
    print("MT5 Data Retrieval via WinRM - Test Script")
    print("=" * 50)
    
    # Connection parameters
    HOST = "13.40.182.210"
    USERNAME = "Administrator"
    
    print("This script requires WinRM to be enabled on the Windows instance.")
    print("Please follow the setup steps in README.md before running this script.\n")
    
    # Test connection
    print("Testing WinRM connection...")
    client = test_winrm_connection(HOST, USERNAME)
    
    if client:
        try:
            # List CSV files
            csv_files = list_mt5_csv_files_winrm(client)
            
            if csv_files:
                print(f"\nFound {len(csv_files)} CSV files")
                
                # Create a directory for retrieved files
                local_download_dir = os.path.join(os.path.dirname(__file__), "retrieved_data")
                
                # Download the CSV files
                download_mt5_csv_files_winrm(client, csv_files, local_download_dir)
            else:
                print("No CSV files found on the remote instance.")
        finally:
            # Note: pypsrp may not have a connection close method
            print("\nConnection test completed.")
    else:
        print("\nCould not establish connection. Please follow the setup instructions in README.md.")

if __name__ == "__main__":
    main()