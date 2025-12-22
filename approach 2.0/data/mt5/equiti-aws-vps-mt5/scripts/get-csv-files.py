import paramiko
import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
ENV_PATH = "/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/mt5/equiti-aws-vps-mt5/.env"
load_dotenv(ENV_PATH)

# Configuration
SSH_HOST = "13.40.182.210"
SSH_PORT = 22
SSH_USERNAME = "Administrator"
SSH_PASSWORD = os.getenv("password")  # Load password from .env
REMOTE_DIR = "C:/Users/Administrator/AppData/Roaming/MetaQuotes/Terminal/DD0DD2E2D928BE723A6D245A160D3117/MQL5/Files"
LOCAL_DIR = "/Users/pawan/CLI-Finance-Terminal/approach 2.0/data/mt5/equiti-aws-vps-mt5/csv_files"

def download_csv_files():
    """Download CSV files from remote Windows server via SFTP"""
    
    # Create local directory if it doesn't exist
    os.makedirs(LOCAL_DIR, exist_ok=True)
    
    # Get list of existing local files
    local_files = set(f for f in os.listdir(LOCAL_DIR) if f.endswith('.csv'))
    logger.info(f"Found {len(local_files)} existing CSV files locally")
    
    try:
        # Validate password is loaded
        if not SSH_PASSWORD:
            raise ValueError("RDP_PASSWORD not found in .env file")
        
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to server using password
        logger.info(f"Connecting to {SSH_HOST}...")
        ssh.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USERNAME,
            password=SSH_PASSWORD,
            timeout=30
        )
        logger.info("Connected successfully!")
        
        # Open SFTP session
        sftp = ssh.open_sftp()
        
        # List remote CSV files
        logger.info(f"Listing files in {REMOTE_DIR}...")
        remote_files = [f for f in sftp.listdir(REMOTE_DIR) if f.endswith('.csv')]
        logger.info(f"Found {len(remote_files)} CSV files on remote server")
        
        # Download new files
        new_files = 0
        for filename in remote_files:
            if filename not in local_files:
                remote_path = f"{REMOTE_DIR}/{filename}".replace('\\', '/')
                local_path = os.path.join(LOCAL_DIR, filename)
                
                logger.info(f"Downloading new file: {filename}")
                sftp.get(remote_path, local_path)
                new_files += 1
            else:
                logger.debug(f"Skipping existing file: {filename}")
        
        if new_files == 0:
            logger.info("No new files to download")
        else:
            logger.info(f"Successfully downloaded {new_files} new file(s)")
        
        # Close connections
        sftp.close()
        ssh.close()
        logger.info("Connection closed")
        
        return new_files
        
    except paramiko.AuthenticationException:
        logger.error("Authentication failed. Check your SSH key.")
        raise
    except paramiko.SSHException as e:
        logger.error(f"SSH connection error: {e}")
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Starting CSV download process...")
        new_count = download_csv_files()
        logger.info(f"Process completed. Downloaded {new_count} new file(s)")
    except Exception as e:
        logger.error(f"Process failed: {e}")
        exit(1)