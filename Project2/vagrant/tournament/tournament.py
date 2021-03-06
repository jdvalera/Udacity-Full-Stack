#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database. Returns a database connection."""
    return psycopg2.connect("dbname=tournament")



def commitQuery(query,args=None,fetch=0):
    """Used to execute INSERT/DELETE queries that require commit 

    Args:
     query: SQL query that you want to execute.
     args: list of arguments
     fetch: 0 - no fetch, 1 - fetchone(), 2 - fetchall()
    """
    temp = None
    db = connect()
    cursor = db.cursor()
    if args == None:
        cursor.execute(query)
    else:
        cursor.execute(query, tuple(args))

    if fetch != 0:
        if fetch == 1:
            temp = cursor.fetchone()
        if fetch == 2:
            temp = cursor.fetchall()
    db.commit()
    db.close()

    return temp
    


def selectQuery(query,args=None,fetch=0):
    """Used to execute SELECT queries that don't require commit
    Args:
     query: SQL query that you want to execute.
     args: list of arguments
     fetch: 0 - no fetch, 1 - fetchone(), 2 - fetchall()
    """
    temp = None
    db = connect()
    cursor = db.cursor()
    if args == None:
        cursor.execute(query)
    else:
        cursor.execute(query, tuple(args))

    if fetch != 0:
        if fetch == 1:
            temp = cursor.fetchone()
        if fetch == 2:
            temp = cursor.fetchall()
    db.close()

    return temp



def deleteMatches():
    """Remove all the match records from the database."""

    query = "DELETE from matches;";
    commitQuery(query)



def deletePlayers():
    """Remove all the player records from the database."""

    query = "DELETE from players;";
    commitQuery(query)



def deleteTournaments():
    """Remove all the tournaments from the database. """

    query = "DELETE FROM tournaments RETURNING id;"
    commitQuery(query)



def deleteRegisteredPlayers():
    """Remove all the registered tournament players. """

    query = "DELETE FROM registeredPlayers;"
    commitQuery(query)



def countPlayers():
    """Returns the number of players currently registered."""

    query = "SELECT count(*) FROM players;";
    return selectQuery(query, None, 1)[0]



def countTournamentPlayers(t_id):
    """Returns the number of players registered in a tournament. """

    query = "SELECT count(*) FROM registeredPlayers WHERE t_id = (%s);";
    return selectQuery(query, [t_id], 1)[0]



def createTournament(name):
    """Creates a tournament.
    Args:
        name: tournament name
    """

    query = "INSERT INTO tournaments (name) VALUES (%s) RETURNING id;"
    t_id = commitQuery(query,[name],1)[0]

    return t_id



def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """

    query = "INSERT INTO players (name) VALUES (%s) RETURNING id;"
    p_id = commitQuery(query,[name],1)[0]

    return p_id



def enterTournament(t_id, p_id):
    """Adds a player and tournament to database.

    Args:
     t_id: tournament id of the tournament which player is being registered to.
     p_id: player id that is being registered
    """

    query = "INSERT INTO registeredPlayers (t_id,p_id) VALUES (%s,%s);"
    commitQuery(query, [t_id,p_id], 0)



def playerStandings(t_id=None):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, 
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains:
     (t_id, p_id, name, wins, draws, score, omw, matches, bye)
        t_id: the id of the tournament the players are registered to
        p_id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        draws: the number of draws the player has
        matches: the number of matches the player has played
        score: the player's score (win=3,lose=0,draw=1)
        oms: Opponent Match Score 
             (collective score of each opponent that the player has played)
        byes: if the player has had a bye 
    """

    if t_id != None:
        query = "SELECT * FROM v_standings WHERE t_id = (%s)";
        rows = selectQuery(query,[t_id],2)
    else:
        query = "SELECT * FROM v_standings;"
        rows = selectQuery(query, None, 2)

    standings = []

    if t_id != None:
        standings = [row for row in rows]
    else:
        for row in rows:
            standings.append((row[1],row[2],row[3],row[5]))

    return standings



def reportMatch(winner, loser=None, t_id = None, draw=False, bye=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    if loser == None:
        bye = True

    query = "INSERT INTO matches (t_id, winner, loser, draw, bye)\
     VALUES (%s,%s,%s,%s,%s);"
    commitQuery(query,[t_id,winner,loser,draw,bye],0)



def checkBye(t_id, p_id):
    """Check if a player has a bye from standings 

    Args:
     t_id: tournament id 
     p_id: player id
    """

    query = "SELECT byes FROM v_standings WHERE id = (%s) AND t_id = (%s);"
    row = selectQuery(query,[p_id,t_id],1)[0]

    if row == 0:
        return False

    return True


def checkMatches(t_id):
    """Return max matches played by everyone in standings 
    
    Args:
     t_id: tournament id 
    """
    query = "SELECT max(matches) FROM v_standings WHERE t_id = (%s);"
    row = selectQuery(query,[t_id],1)[0]


    return row
 

 
def swissPairings(t_id = None):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    If there is an odd number of players a player will be assigned a bye. Then
    players are paired depending on their wins. To allow every player to have
    the same number of matches a player is popped off the list for pairing 
    cosideration.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    rows = playerStandings(t_id)
    temp = []
    if t_id != None:
        numPlayers = countTournamentPlayers(t_id)
    else:
        numPlayers = countPlayers()

    matchNum = checkMatches(t_id)


    """ Checks if there are odd number of players. A bye is given to a player
        that doesn't have a bye yet. It also gives a bye to the player with the
        least amount of matches to keep matches even per player.
    """
    if numPlayers%2 != 0:
        for i in range(numPlayers-1, 0, -1):
            if checkBye(rows[i][0], rows[i][1]) == False \
            and rows[i][5] < matchNum:
                reportMatch(rows[i][1], None ,rows[i][0])
                break
    
    """ Update the standings accounting for the given bye. """
    rows = playerStandings(t_id)

    """ Pop off a player from the standings that hasn't had a bye yet. To
        ensure that every player has equal amount of matches played, the 
        player removed from the list isn't a player that has less matches
        than every other player.
    """
    if numPlayers%2 != 0:
        for i in range(0, numPlayers-1, 1):
            if checkBye(rows[i][0], rows[i][1]) == False \
            and rows[i][5] >= matchNum:
                rows.pop(i)
                numPlayers = numPlayers-1
                break   

    if t_id != None:
        temp = [(rows[i][1],rows[i][2],rows[i+1][1],rows[i+1][2])for \
         i in range(0,numPlayers-1,2)]
    else:
        temp = [(rows[i][0],rows[i][1],rows[i+1][0],rows[i+1][1])for \
         i in range(0,numPlayers-1,2)]    

    return temp