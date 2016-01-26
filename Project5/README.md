Linux Server Configuration
=====================
by John Valera, in fulfillment of [Udacity's Full Stack Web Developer Nanodegree]
 (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)


### About
Took a baseline installation of a Linux distribution on a virtual machine and prepared it to host a web application by installing updates, securing it from a number of attack vectors and installing/configuring web and database servers.

Server Info:
- Public IP: `52.35.200.181`
- SSH Port: `2200`
- Project Url: [http://ec2-52-35-200-181.us-west-2.compute.amazonaws.com/][1]

## Configurations

### Basic Configuration

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
7. Update all installed packages
  - Find updates using: `sudo apt-get update`
  - Install updates using: `sudo apt-get upgrade`
8. Set timezone to UTC
  - Type `sudo dpkg-reconfigrue-tzdata` from the prompt select 'none of the above' and then select UTC.

### Firewall Configuration

1. Configure the Uncomplicated Firewall (UFW) to allow all outgoing connections and only allow connections for SSH, HTTP and NTP.
2. Check Firewall status 
  - Use `sudo ufw status` to see if Firewall is inactive or not.
3. Configure the Firewall to deny all incoming by default
  - `sudo ufw default deny incoming`
4. Set Firewall to allow all outgoing connections
  - `sudo ufw default allow outgoing`
5. Allow ssh
  - By default ssh is port 22 but we changed it to port 2200 so we use `sudo ufw allow 2200/tcp`
6. Allow HTTP
  - `sudo ufw allow 80/tcp`
7. Allow NTP
  - `sudo ufw allow 123`
8. Enable Firewall
  - `sudo ufw enable`
 
### Apache and Flask Configuration

1. Install apache
  - `sudo apt-get install apache2` 
2. Install mod_wsgi
  - `sudo apt-get install libapache2-mod-wsgi`
3. Enable mod_wsgi
  - `sudo a2enmod wsgi`
4. Install and configure Flask
  - Install pip first: `sudo pip apt-get install python-pip`
  - Then install Flask: `sudo pip install Flask`
  - Go into the www directory: `cd /var/www`
  - Create a 'catalog' directory: `sudo mkdir catalog`
  - Go into the created 'catalog' directory: `cd catalog`
  - Create another 'catalog' directory: `sudo mkdir catalog`
  - Inside this second 'catalog' directory is where the web application will be placed
5. Create a configuration file to allow Apache to serve our Flask application
  - `sudo nano /etc/apache2/sites-available/catalog.conf`
  - The `catalog.conf` file contains info about the web application such as the server name, server admin, and directories used
6. Enable the web app that the `catalog.conf` file refers to
  - `sudo a2ensite catalog`
7. Create a .wsgi File which Apache uses to serve the Flask app
  - `sudo nano catalog.wsgi`
  - The `catalog.wsgi` file runs the Flask application
8. Restart Apache
  - `sudo service apache2 restart`

### Git
1. Cloned GIT rep from [Project 3][2] inot `/home/grader/` and copied the directory into `/var/www/catalog/catalog`
2. Made sure that `etc/apache2/apache2.conf` had `AllowOverride All` for the `var/www/` directory to allow htaccess files
3. Added a .htaccess file in `/var/www/catalog/catalog/mygoals` (Root directory of webpage)
  - Inside the .htaccess file: `RedirectMatch 404/\.git` to ensure that the .git directory is inaccessible
  - Also inside the .htaccess file: `Options -Indexes` to disallow access to the /static directory

[1]: [http://ec2-52-35-200-181.us-west-2.compute.amazonaws.com/]
[2]: [https://github.com/jdvalera/Udacity-Full-Stack/tree/master/Project3]
