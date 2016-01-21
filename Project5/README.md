Linux Server Configuration
=====================
by John Valera, in fulfillment of [Udacity's Full Stack Web Developer Nanodegree]
 (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)


### About
Took a baseline installation of a Linux distribution on a virtual machine and prepared it to host a web application by installing updates, securing it from a number of attack vectors and installing/configuring web and database servers.

## Configurations

### Basic Tasks
1. Created user 'grader' using `sudo adduser grader`.
2. Gave 'grader' sudo privileges by adding a file `grader` with the following line `grader ALL=(ALL) NOPASSWD:ALL` to `/etc/sudoers.d`.
3. Change SSH port from default 22 to 2200
  - Updated 'sshd_config' using `sudo nano /etc/ssh/sshd_config` and changing port 22 to port 2200.
4. Create SSH key pair for user grader
  - On local machine generate SSH key pair with `ssh-keygen`
  - Save the keygen file in the ssh directory `/Users/username/.ssh/`
  - Log in to the server as user 'grader.
5. 

