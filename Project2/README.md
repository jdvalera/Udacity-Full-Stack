Tournament Planner
=====================
by John Valera, in fulfillment of [Udacity's Full Stack Web Developer Nanodegree] (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)

###About

The project contains a Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament. 

The game tournament uses the Swiss system for pairing up players in each round: players are not eliminated, and each plaer should be paired with another player with the same number of wins, or as close as possible. A configured Vagrant virtual machine along with python skeleton files are provided by Udacity.

###Features

1. Supports odd number of players by assigning one player a "bye" (skipped round) which counts as a free win.
2. Support games where a draw (tied game) is possible.
3. Uses a scoring system (Win - 3pts, Loss - 0pts, Draw - 1pts)
4. When two players have the same number of wins, they are ranked according to OMS (Opponent Match Score), the total number of points by players they have played against. (**Note:** OMW (Opponent Match Wins) was replaced with OMS (Opponent Match Score) as it makes more sense to use a players score instead of their wins as a tiebreaker)
5. Supports more than one tournament in the database, so matches do not have to be deleted between tournamnets.
