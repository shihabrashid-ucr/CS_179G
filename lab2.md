
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

 ## One step access to EC2 instance
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
5. Create a shortcut to the EC2 instance, by adding one entry to `~/.ssh/config`. Open and edit the config file
6. Add the following content to the config file
	```
	Host alias_name 
	  HostName cs179g-fall-2022-0#.cs.ucr.edu
	  User ubuntu
	  IdentityFile ~/.ssh/id_rsa_cs179g
	  ProxyCommand ssh -W %h:%p -i ~/.ssh/id_rsa_cs179g ucr_net_id@bolt.cs.ucr.edu
	```
	*alias_name* is your preferred name, you may just set it to `cs179g`. Replace `#`  in the HostName field with your group number.
7. Try
	```bash
	ssh alias_name  # ssh cs179g
	```

### Windows
1. In WinSCP, go to **Options**, then **Preferences**
2. Select **Panels** from the left
3. Check **Show hidden files** under **Common**, then **OK**
4. Now you can see hidden files on bolt. Those files' names have a common prefix `.`
5. On bolt, go to `/extra/cs179g/ucr_net_id`, you will find 4 files there: *config*,  *group*, *id_rsa* and *id_rsa.pub*
6. Open PuTTY, run the following command
	```bash
	cat /extra/cs179g/$LOGNAME/id_rsa.pub >> ~/.ssh/authorized_keys
	chmod 0600 ~/.ssh/authorized_keys
	```
7. Download **id_rsa** to your local machine
8. Find and open **PuTTYgen** in the start menu (under PuTTY)
9. Click **Load** button and select the **id_rsa** file you just downloaded
10. Click **Save private key** to save it as a new file, like `id_rsa.ppk`. You don't need to set a passphrase
11. In WinSCP, create a new site, set **Host name** to `cs179g-fall-2021-0#.cs.ucr.edu`, where `#` is your group number; set **User name** to `ubuntu`, leave the **Password** empty
12. Click **Advanced**, then select **SSH** and **Authentication** on the left, under **Private key file**, select the key you just saved (`id_rsa.ppk`)
Ref: [https://winscp.net/eng/docs/ui_login_authentication](https://winscp.net/eng/docs/ui_login_authentication)
13. Select **Connection** and **Tunnel**, check **Connect through SSH tunnel**, and enter the following information
	- Host name: `bolt.cs.ucr.edu`
	- User name: `ucr_net_id`
	- Password: leave empty
	- Private key file: select the same key (`id_rsa.ppk`)
Ref: [https://winscp.net/eng/docs/ui_login_tunnel](https://winscp.net/eng/docs/ui_login_tunnel)
14. **OK** and then **Save** the site. You may name the site to `cs179g`
15. Now you can directly login to your EC2 instance. If you open PuTTY from there, the command line is for your EC2 instance

## Setup JupyterLab
JupyterLab provides a web interface for you to create, edit and run Python notebook files. It also allows to edit text files or run commands from the built-in command line. Which means, you don't need SSH access or file transfers via command line or WinSCP+PuTTY anymore.

1. Refer to the first lab to create a virtual environment
2. Install JupyterLab in the virtual environment, you must use port `8888` during the setup
	- You may copy the settings file to your local machine to edit and transfer it back
	- To transfer a remote file to your local machine, run `scp cs179g:remote_file_path local_file_path`
	- To transfer a local file to the EC2 instance, run `scp local_file_path cs179g:remote_file_path`
3. Install JupyterLab as system service
4. Visit JupyterLab via `http://cs179g-fall-2021-0#.cs.ucr.edu:8888`. If you are off-campus, you must use the [campus VPN](https://ucrsupport.service-now.com/ucr_portal/?id=kb_article&sys_id=8a264d791b5f0c149c0b844fdd4bcb34)

## Other notes
- Since the same instance is used by all group members, make sure only one is installing necessary software and packages, and let the others know what you have installed.
-  Try to coordinate to avoid editing the same file(s).
-  If you want to have some personal files for testing, you can create a directory with your name under the home directory `/home/ubuntu`.
-  JupyterLab must run on port `8888`.
-  The web server in part 3 must run on port `8080`.
