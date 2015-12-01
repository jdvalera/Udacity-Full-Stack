Goal Catalog
=====================
by John Valera, in fulfillment of [Udacity's Full Stack Web Developer Nanodegree]
 (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)

### About

This web app allows users to list their goals and share it with others. The 
application provides a user registration and authentication system implementing 
a third-party authentication and authorization service. Registered users will 
have the ability to create, edit, update and delete their goals. The application 
is programmed in Python using Flask along with 
SQLAlchemy.

### Frameworks/Libraries/Technologies used:

* Flask
* Jinja2
* SQLAlchemy
* Flask-SeaSurf

### How to Run
1. Install VirtualBox and Vagrant. You might also need to install Git if you are 
using Windows as you would need to use Git Bash to access the virtual machine.
2. Clone this repo `git clone https://github.com/jdvalera/Udacity-Full-Stack.git`
 and navigate to the vagrant folder in the Project3 directory: `cd Project3/vagrant/`
3. Type `vagrant up` to launch the virtual machine. This will download dependencies
if it is your first time executing this command so you might need to wait a while.
4. Once it is up and running, type vagrant ssh to log into the virtual machine.
5. Once inside the virtual machine, navigate to the catalog directory. `cd /vagrant/catalog/`
6. Inside the catalog directory type `python database_setup.py` to initialize the database.
7. After initializing the database type `python project.py` to launch the application.
8. You can now view the page from your browser at [http://localhost:5000](http://localhost:5000).
