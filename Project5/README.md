Linux Server Configuration
=====================
by John Valera, in fulfillment of [Udacity's Full Stack Web Developer Nanodegree]
 (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)


### About
Took a baseline installation of a Linux distribution on a virtual machine and prepared it to host a web application by installing updates, securing it from a number of attack vectors and installing/configuring web and database servers.

Server Info:
- Public IP: `52.35.200.181`
- SSH Port: `2200`
- Project Url: [http://ec2-52-35-200-181.us-west-2.compute.amazonaws.com/](1)

## Packages Installed

* git
* apache2
* postgresql
* postgresql-contrib
* python-flask
* python-psycopg2
* python-pip
* python-sqlalchemy
* flask-seasurf
* httplib2
* finger
* libapache2-mod-wsgi
* python-dev
* virtualenv
* oauth2client
* werkzeug
* google-api-python-client
* jinja2
* fail2ban
* unattended-upgrades
* sendmail
* glances

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
1. Install Git:
  - `sudo apt-get install git`
  - `git config --global user.name "YOURNAME"`
  - `git config --global user.email "YOU@DOMAIN.COM"`
2. Cloned GIT rep from [Project 3](2) into `/home/grader/` and copied the directory into `/var/www/catalog/catalog`
3. Made sure that `etc/apache2/apache2.conf` had `AllowOverride All` for the `var/www/` directory to allow htaccess files
4. Added a .htaccess file in `/var/www/catalog/catalog/mygoals` (Root directory of webpage)
  - Inside the .htaccess file: `RedirectMatch 404/\.git` to ensure that the .git directory is inaccessible
  - Also inside the .htaccess file: `Options -Indexes` to disallow access to the /static directory

### PostgreSQL
1. Install PostgreSQL
  - `sudo apt-get update`
  - `sudo apt-get install postgresql postgresql-contrib`
2. PostgreSQL is configured by default to not allow remote connections
3. Create role `catalog`
  - Upon installation, Postgres creates a Linux user called "postgres" which can be used to access the system
  - Log in to PostgreSQL by first switching to the postgres user `sudo su - postgres` and then typing `psql`
  - Type `CREATE ROLE catalog WITH CREATEDB CREATEROLE SUPERUSER LOGIN PASSWORD 'catalog';`
  - The above statement creates a catalog superuser role with the ability to create databases and roles with a login password of 'catalog'
4. Create a database `catalog`
  - `CREATE DATABASE catalog WITH OWNER catalog;`
5. `python engine = create_engine('postgresql://catalog:"db-password":localhost/catalog')`

### Automatic Updates
1. Install unattended-upgrades
  - `sudo apt-get install unattended-upgrades`
  - enable using `sudo dpkg-reconfigure -plow unattended-upgrades`

### Glances for monitoring
1. Install glances
  - `sudo pip install Glances`
2. Run glances with:
  - `glances`

### Monitoring SSH Login Attempts
1. Used Fail2ban to monitor login attempts on SSH and ban ip addresses on failed login attempts
2. Install Fail2ban
  - `sudo apt-get install fail2ban`
  - Copy config file to .local `sudo cp /etc/fail2ban/jail.con /etc/fail2ban/jail.local`
  - You can change some settings in the jail.local file
  - Change `destemail = YOURNAME@DOMAIN`
  - Change `action = %(action_mwl)s` to configure Fail2ban to email you on failed login attempts with a log
  - Change port number under ssh to `port = 2200`
3. Stop and start fail2ban service:
  - `sudo service fail2ban stop`
  - `sudo service fail2ban start`
4. Testing Fail2ban:
  - Allow password-base logins by editing `/etc/ssh/sshd_config`
  - Edit `/etc/fail2ban/jail.local` and change the destemail to your email addresss
  - Stop and start the fail2ban service
   * `sudo service fail2ban stop`
   * `sudo service fail2ban start`
  - Try to login with a random user like: `ssh blah@52.35.200.181 -p 2200` and type random passwords until you stop seeing "Permission denied messages"
  - Check your email and you should be notified about the ban
  - You can also run `sudo iptables -S` to see the banned address
  - Make sure to disable password-base logins after testing

### Resources
[Automatic Security Updates](3)

[Change Timezone](4)

[How To Protect SSH with Fail2Ban on Ubuntu 14.04](5)

[How To Install and Use PostgreSQL on Ubuntu 14.04](6)

[How To Deploy a Flask Application on an Ubuntu VPS](7)

[Deploy Your Flask App to Heroku](8)

[Make .git directory inaccessible](9)

[Install Apache](10)

[Glances](11)

[Apache Disable indexes](12)

[How To Use the .htaccesss File](13)

[1]: [http://ec2-52-35-200-181.us-west-2.compute.amazonaws.com/]
[2]: [https://github.com/jdvalera/mygoals]
[3]: [https://help.ubuntu.com/community/AutomaticSecurityUpdates]
[4]: [https://help.ubuntu.com/community/UbuntuTime#Using_the_Command_Line_.28terminal.29]
[5]: [https://help.ubuntu.com/community/UbuntuTime#Using_the_Command_Line_.28terminal.29]
[6]: [https://help.ubuntu.com/community/UbuntuTime#Using_the_Command_Line_.28terminal.29]
[7]: [https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps]
[8]: [https://www.udacity.com/wiki/ud330/deploy]
[9]: [http://stackoverflow.com/questions/6142437/make-git-directory-web-inaccessible]
[10]: [https://www.digitalocean.com/community/tutorials/how-to-install-linux-apache-mysql-php-lamp-stack-on-ubuntu]
[11]: [http://glances.readthedocs.org/en/latest/glances-doc.html#configuration]
[12]: [http://www.ducea.com/2006/06/26/apache-tips-tricks-disable-directory-indexes/]
[13]: [https://www.digitalocean.com/community/tutorials/how-to-use-the-htaccess-file]
