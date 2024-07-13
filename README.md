1. Scrip task

For this I decided to go with bash and python, bash for the initial retrieval of the user information and python for the processing. I wrote it to my git on a public repo, and deployed via Jenkins running on a GKE cluster (that was spun up via an orchestration that I wrote, links will be at the end of the project)

`#!/bin/bash`

`cat /etc/passwd | awk -F: '{print $1 ":" $6}'`

Firstly we have a shebang, to let the system know that this script needs execution in bash shell.
I knew the /etc/passwd file from my experience with linux but I used the awk man page and google to see how to use awk to take only the required text from the passwd output.

*output from my cloud instance running ubuntu 24.04*

`cat /etc/passwd` 

`root:x:0:0:root:/root:/bin/bash`
`daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin`
`bin:x:2:2:bin:/bin:/usr/sbin/nologin`
`sys:x:3:3:sys:/dev:/usr/sbin/nologin`
`sync:x:4:65534:sync:/bin:/bin/sync`
`games:x:5:60:games:/usr/games:/usr/sbin/nologin`

`-F:` sets the field separator to colon 

 `'{print $1 ":" $6}'` tells awk to print the first field ($1) and sixth ($6) with a colon ":" between, a colon
 In /etc/passwd, the first field is the username and the sixth field is the home directory

`cat /etc/passwd | awk -F: '{print $1 ":" $6}'`

`root:/root`
`daemon:/usr/sbin`
`bin:/bin`
`sys:/dev`
`sync:/bin`
`games:/usr/games`

https://man7.org/linux/man-pages/man1/awk.1p.html
https://www.tim-dennis.com/data/tech/2016/08/09/using-awk-filter-rows

I decided to do the remainder of the operation in python, the script will be posted below. underneath it will be a line by line breakdown and my choices/sources for the exact code used.

`import hashlib`
`import subprocess`
`from datetime import datetime`
`import os`

`def get_user_list_hash():`
    `result = subprocess.run(['bash', 'list_users.sh'], capture_output=True, text=True)`
    `return hashlib.md5(result.stdout.encode()).hexdigest()`

`def main():`
    `current_hash = get_user_list_hash()`
    
    `if not os.path.exists('/var/log/current_users'):`
        `with open('/var/log/current_users', 'w') as f:`
            `f.write(current_hash)`
    `else:`
        `with open('/var/log/current_users', 'r') as f:`
            `stored_hash = f.read().strip()`
        
        `if current_hash != stored_hash:`
            `now = datetime.now()`
            `date_time = now.strftime("%Y-%m-%d %H:%M:%S")`
            
            `with open('/var/log/user_changes', 'a') as f:`
                `f.write(f"{date_time} changes occurred\n")`
            
            `with open('/var/log/current_users', 'w') as f:`
                `f.write(current_hash)`

`if __name__ == "__main__":`
    `main()`


**Code breakdown**


These are the libraries i decided to go with, I chose hashlib for hashing after checking google. I chose subprocess because it is a more secure way to run the bash script (as os.system could be vulnerable to injection)

`import hashlib`
`import subprocess`
`from datetime import datetime`
`import os`

the following function uses the subprocess library to run the list_user.sh script in bash and capture the output, then running it through the hashlib md5 module. I knew subprocess from my personal experience doing automation in python and i learnt about hashlib using youtube as a starting point https://www.youtube.com/watch?v=SVmZZK11Tjc

`def get_user_list_hash(): result = subprocess.run(['bash', 'list_users.sh'], capture_output=True, text=True) return hashlib.md5(result.stdout.encode()).hexdigest()`

Next is our main function, which I will break the logic of step by stop. First we define the main function and set a variable named current_hash to be the result of the get_user_list_hash function. Thus triggering it to run.

`def main():`
	`current_hash = get_user_list_hash()`

Then we will do an if check to see if the current_user file exists, if not the file is created using open and the current hash is written to it.

`if not os.path.exists('/var/log/current_users'):`
        `with open('/var/log/current_users', 'w') as f:`
            `f.write(current_hash)`

If the file does exist we will compare the results of the get_user_list_hash function with the file. firstly by reading the file and storing its values as stored_hash

`else:`
        `with open('/var/log/current_users', 'r') as f:`
            `stored_hash = f.read().strip()`

afterwards we have an if statement which will decide if we enter the conditional block, we want to see if current_hash and stored_hash are different so we use `!=` which is not equal. If that's the case then the users list changed and the conditional block is entered. we take the current time using datetime library and store it as variable `now`. then we save that variable as a string, I did this using string format time (Pretty handy and I used it before).

`if current_hash != stored_hash:`
            `now = datetime.now()`
            `date_time = now.strftime("%Y-%m-%d %H:%M:%S")`

Finally we wrap up the script by doing two things, updating that changes occurred in a separate file and writing current_hash into the current_users file.

	`with open('/var/log/user_changes', 'a') as f:`
                `f.write(f"{date_time} changes occurred\n")`
        `with open('/var/log/current_users', 'w') as f:`
                `f.write(current_hash)`


I kept this script simple but based on the use case a more robust error handling could be used. to handle errors from file corruption, retrieval of datetime etc
Also I included a main check to keep this as a script and not a module.

The crontab entry is as follows : 


`0 * * * * /bin/bash /path/to/list_users.sh | /usr/bin/python3 /path/to/check_users.py`


`0 * * * *` is our schedule, making the script run in minute 0 of every hour.
then we specify that bash is the executor and the path to the bash script, its piped into the check_users.py script with python3 being the executor.
