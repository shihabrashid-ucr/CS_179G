
# CS 179G Lab - SSH to EC2

## Campus VPN
[Campus VPN](https://ucrsupport.service-now.com/ucr_portal/?id=kb_article&sys_id=8a264d791b5f0c149c0b844fdd4bcb34) is required to access the EC2 instance in a web browser. Make sure you connect to the VPN.

## Connect to bolt
You need a gateway server to connect to your group's EC2 instance. If you have used `bolt.cs.ucr.edu` before, you may skip this section.

### Linux and MacOS
1. Open a terminal
2. Enter `ssh ucr_net_id@bolt.cs.ucr.edu`, replace `ucr_net_id` with your UCR net ID
3. When asked "*Are you sure you want to continue connecting (yes/no/[fingerprint])?*", type `yes` and Enter
4. Enter your CS account's password
5. You shall see `ucr_net_id@bolt $`

### Windows
(For Older Windows)
1. Download and install PuTTY from [https://www.putty.org/](https://www.putty.org/). This gives you command line interface to SSH to a remote server
2. Download and install WinSCP from [https://winscp.net/eng/index.php](https://winscp.net/eng/index.php). This is a GUI tool for file transfer via SSH
3. Open WinSCP, select **New Site** from the left panel
4. In the right panel, put `bolt.cs.ucr.edu` into **Host name**, your UCR net ID into **User name**, and enter your CS account's password into **Password**, leave the other fields unchanged
5. Save this site setting by clicking **Save**. You can choose to save the password. You may set the site name to `bolt`
6. Select the site you just created from the left panel, click **Login**
7. Now you are on **bolt**
8. Find an icon in the toolbar with 2 monitors and a flash symbol. It should be the second button after **Synchronize**. This will open an interactive terminal via PuTTY

To SSH to your group's EC2 instance, type `cs179g_login`
You should see some message from your EC2 instance and `ubuntu@ip-###-###-###-###:~$`. The user name is `ubuntu` (default).

(For newer Windows)
Open the search option in `start` and type `PowerShell`. PowerShell is equivalent to the `terminal` on linux based systems. Follow the steps of Linux once PowerShell is opened.

 ## One step access to EC2 instance and VsCode (Optional but highly recommended)
 In the previous step, you can SSH to your EC2 instance by first login to bolt then `cs179g_login`. This whole process can be simplified into a single step operation (or single command).

### Linux and MacOS
1. SSH to bolt. If you are on the EC2 instance, you can type `exit` to go back to bolt
2. Type the following command to copy the auto-generated public key for keyless access
	```bash
	cat /extra/cs179g/$LOGNAME/id_rsa.pub >> ~/.ssh/authorized_keys
	chmod 0600 ~/.ssh/authorized_keys
	exit
	```
3. Run the following command (from your local machine) to copy the auto-generated SSH keys to your local machine from bolt
	```bash
	if [[ ! -d ~/.ssh ]]; then mkdir ~/.ssh; chmod 0700 ~/.ssh; fi
	scp ucr_net_id@bolt.cs.ucr.edu:/extra/cs179g/ucr_net_id/id_rsa ~/.ssh/id_rsa_cs179g
	chmod 0600 ~/.ssh/id_rsa_cs179g
	```
4. Try SSH to bolt to see if it requires a password
	```bash
	ssh ucr_net_id@bolt.cs.ucr.edu
	```
	If it does not work, try
	```bash
	ssh -i ~/.ssh/id_rsa_cs179g ucr_net_id@bolt.cs.ucr.edu
	```
On your local computer,
   Create a shortcut to the EC2 instance, by adding one entry to `~/.ssh/config`. Open and edit the config file
   Add the following content to the config file
	```
	Host alias_name 
	  HostName cs179g-fall-2023-0#.cs.ucr.edu
	  User ubuntu
	  IdentityFile ~/.ssh/id_rsa_cs179g
	  ProxyCommand ssh -W %h:%p -i ~/.ssh/id_rsa_cs179g ucr_net_id@bolt.cs.ucr.edu
	```
	*alias_name* is your preferred name, you may just set it to `cs179g`. Replace `#`  in the HostName field with your group number.
Now, Try
	```bash
	ssh alias_name  # ssh cs179g
	```

### Windows
1. SSH to bolt. If you are on the EC2 instance, you can type `exit` to go back to bolt
2. Type the following command to copy the auto-generated public key for keyless access
	```bash
	cat /extra/cs179g/$LOGNAME/id_rsa.pub >> ~/.ssh/authorized_keys
	chmod 0600 ~/.ssh/authorized_keys
	exit
	```
3. On your local computer, open `PowerShell` and type
```bash
scp ucr_net_id@bolt.cs.ucr.edu:/extra/cs179g/ucr_net_id/id_rsa <ANY YOUR WINDOWS LOCAL PATH>
```
Remember this path that you just saved the `id_rsa` file to.
4. Open VSCode, open the file `Users/user_id/.ssh/config`, there type:
Add the following content to the config file
	```
	Host alias_name 
	  HostName cs179g-fall-2023-0#.cs.ucr.edu
	  User ubuntu
	  IdentityFile ~/.ssh/id_rsa_cs179g
	  ProxyCommand ssh -W %h:%p -i ~/.ssh/id_rsa_cs179g ucr_net_id@bolt.cs.ucr.edu
	```
	*alias_name* is your preferred name, you may just set it to `cs179g`. Replace `#`  in the HostName field with your group number.
 Now try the following in PowerShell:
	```bash
	ssh alias_name  # ssh cs179g
	```

Download and Install VSCode. Install `Remote-SSH` extension in VSCode. Now you will be able to open and code in lab server directly from vscode.

## Initial Setup
```bash
sudo apt-get update
sudo apt-get -y dist-upgrade
```

## Create virtual environment
Install conda.
```bash
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash
~/miniconda3/bin/conda init zsh
```
Exit the server by typing `exit` and login to server again. Check whether conda is installed properly by typing `conda list`. If it shows some list then it is installed correctly.

Create new environment:
```bash
conda create -n myenv python=3.10
# Replace myenv with the name you want
```
Enter new environment:
```bash
conda activate myenv
```
Install `pip`:
```bash
sudo apt install python3-pip
```
**Exit Virtual Environment**
```bash
conda deactivate
```

## Install JupyterLab (Optional - If VSCode does not work)
Reference: [https://www.digitalocean.com/community/tutorials/how-to-set-up-a-jupyterlab-environment-on-ubuntu-18-04](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-jupyterlab-environment-on-ubuntu-18-04)

In virtual environment
```bash
python3 -m pip install jupyterlab
pip3 install markupsafe==2.0.1
sudo -H pip install jupyter
# Create a default config file
jupyter notebook --generate-config
# Create a password. Your hashed password is stored in ~/.jupyter/jupyter_server_config.json
jupyter notebook password
```

Edit *~/.jupyter/jupyter_notebook_config.py*, uncomment and edit the following settings
```
c.ServerApp.ip = '*'
c.ServerApp.open_browser = False
c.ServerApp.password = 'your_hashed_password'
c.ServerApp.port = 8888
```

Run JupyterLab
```
jupyter lab --ip 0.0.0.0 --port 8888
```

Test in your browser
Visit [http://cs179g-fall-2023-0#.cs.ucr.edu:8888](http://cs179g-fall-2023-0#.cs.ucr.edu:8888) (Replace # with your group number)

**Please remember to close the server using `ctrl+C`.

## Kill a process

```
kill -9 $(lsof -t -i:8888)
```

## Other notes
- Since the same instance is used by all group members, make sure only one is installing necessary software and packages, and let the others know what you have installed.
-  Try to coordinate to avoid editing the same file(s).
-  If you want to have some personal files for testing, you can create a directory with your name under the home directory `/home/ubuntu`.
-  JupyterLab must run on port `8888`.
-  The web server in part 3 must run on port `8080`.
