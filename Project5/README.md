Linux Server Configuration
=====================
by John Valera, in fulfillment of [Udacity's Full Stack Web Developer Nanodegree]
 (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)


### About
Took a baseline installation of a Linux distribution on a virtual machine and prepared it to host a web application by installing updates, securing it from a number of attack vectors and installing/configuring web and database servers.

## Configurations

### Basic Tasks
1. Created user 'grader' using `sudo adduser grader`.
2. Gave 'grader' sudo privileges
  - Add a file `grader` with the following line `grader ALL=(ALL) NOPASSWD:ALL` to `/etc/sudoers.d`
3. Change SSH port from default 22 to 2200
  - Updated 'sshd_config' using `sudo nano /etc/ssh/sshd_config` and changing port 22 to port 2200
4. Create SSH key pair for user grader
  - On local machine generate SSH key pair with `ssh-keygen`
  - Save the keygen file in the ssh directory `/Users/<username>/.ssh/`
  - Log in to the server as user 'grader'
  - Check to see if there is a .ssh directory using `ls -a`, if not create one using `mkdir .ssh`
  - In the .ssh folder create a file 'authorized_keys' using `nano .ssh/authorized_keys` to store your public keys
  - On your local machine read the contents of your public key using `cat .ssh/\<keyname\>.pub
  - Copy and paste the public key to the 'authorized_keys' file using `nano .ssh/authorized_keys`
  - Set permissions for files using: `chmod 700 .ssh` and `chmod 644 .ssh/authorized_keys`
  - You can now log in with the key pair: `ssh grader@\<Public IP Address of Server\> -p 2200 -i ~/.ssh
5. Force Key Based Authentication
  - Edit 'sshd_config' file using `sudo nano /etc/ssh/sshd_config` find `PasswordAuthentication` and edit it to `PasswordAuthentication no`
  - Refresh sshd to run new configuration using `sudo service ssh restart`
6. Disable Root Login
  - Edit 'sshd_config' file using `sudo nano /etc/ssh/sshd_config`, find and edit `PermitRootLogin` to `PermitRootLogin no`
  - Refresh sshd `sudo service ssh restart` to run new configuration
7.

