Tournament Planner
=====================
by John Valera, in fulfillment of [Udacity's Full Stack Web Developer Nanodegree] (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)

###About

The project contains a Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament. The project uses Python 2.7.  

The game tournament uses the Swiss system for pairing up players in each round: players are not eliminated, and each plaer should be paired with another player with the same number of wins, or as close as possible. A configured Vagrant virtual machine along with python skeleton files are provided by Udacity.

###Features

1. Supports odd number of players by assigning one player a "bye" (skipped round) which counts as a free win.
2. Support games where a draw (tied game) is possible.
3. Uses a scoring system (Win - 3pts, Loss - 0pts, Draw - 1pts)
4. When two players have the same number of wins, they are ranked according to OMS (Opponent Match Score), the total number of points by players they have played against. (**Note:** OMW (Opponent Match Wins) was replaced with OMS (Opponent Match Score) as it makes more sense to use a player's score instead of their wins as a tiebreaker)
5. Supports more than one tournament in the database, so matches do not have to be deleted between tournamnets.

###Project Package

* **tournament.sql** - Used to set up the database. Constains SQL queries that creates the database.
* **tournament.py** - This file is used to provide access to the database via a library of functions which can add, delete, or query data in the database.
* **tournament_test.py** - A client program that uses the tournament.py module. This was provided by Udacity to test the implementation of the functions in tournament.py. **Note:** Since extra features were added, this file has been changed to function correctly with the added features.

###How to Run

1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/downloads). You might also need to install [Git](http://git-scm.com/downloads) if you are using Windows as you would need to use Git Bash to access the virtual machine.
2. Clone this repo `git clone https://github.com/jdvalera/Udacity-Full-Stack.git` and navigate to the vagrant folder in the Project2 directory: `cd Project2/vagrant/`
3. Type `vagrant up` to launch the virtual machine. This will download dependecies if it is your first time executing this command so you might need to wait a while. 
4. Once it is up and running, type `vagrant ssh` to log into the virtual machine. 
5. Once inside the virtual machine, navigate to the tournament directory. `cd /vagrant/tournament/`
6. Inside the tournament folder, create the database by running psql. `psql -f tournament.sql`
7. Run tournament_test.py `python tournament_test.py`

