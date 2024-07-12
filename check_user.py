import hashlib
import subprocess
from datetime import datetime
import os

def get_user_list_hash():
    result = subprocess.run(['bash', 'list_users.sh'], capture_output=True, text=True)
    return hashlib.md5(result.stdout.encode()).hexdigest()

def main():
    current_hash = get_user_list_hash()
    
    if not os.path.exists('/var/log/current_users'):
        with open('/var/log/current_users', 'w') as f:
            f.write(current_hash)
    else:
        with open('/var/log/current_users', 'r') as f:
            stored_hash = f.read().strip()
        
        if current_hash != stored_hash:
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            
            with open('/var/log/user_changes', 'a') as f:
                f.write(f"{date_time} changes occurred\n")
            
            with open('/var/log/current_users', 'w') as f:
                f.write(current_hash)

if __name__ == "__main__":
    main()