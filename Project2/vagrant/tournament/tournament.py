#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database. Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    cursor = db.cursor()
    query = "DELETE from matches;";
    cursor.execute(query)
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    cursor = db.cursor()
    query = "DELETE from players;";
    cursor.execute(query)
    db.commit()
    db.close()

def deleteTournaments():
    """Remove all the tournaments from the database. """
    db = connect()
    cursor = db.cursor()
    query = "DELETE FROM tournaments RETURNING id;"
    cursor.execute(query)
    db.commit()
    db.close()


def deleteRegisteredPlayers():
    """Remove all the registered tournament players. """
    db = connect()
    cursor = db.cursor()
    query = "DELETE FROM registeredPlayers;"
    cursor.execute(query)
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    cursor = db.cursor()
    query = "SELECT count(*) from players;";
    cursor.execute(query)
    rows = cursor.fetchall()
    db.close()
    return rows[0][0]

def countTournamentPlayers(t_id):
    """Returns the number of players registered in a tournament. """
    db = connect()
    cursor = db.cursor()
    query = "SELECT count(*) from registeredPlayers WHERE t_id = (%s);";
    cursor.execute(query, (t_id, ))
    rows = cursor.fetchall()
    db.close()
    return rows[0][0]


def createTournament(name):
    """Creates a tournament.
    Args:
        name: tournament name
    """
    db = connect()
    cursor = db.cursor()
    query = "INSERT INTO tournaments (name) VALUES (%s) RETURNING id;"
    cursor.execute(query, (name,))
    t_id = cursor.fetchone()[0]
    db.commit()
    db.close()

    return t_id


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    cursor = db.cursor()
    query = "INSERT INTO players (name) VALUES (%s) RETURNING id;"
    cursor.execute(query, (name, ))
    p_id = cursor.fetchone()[0]
    db.commit()
    db.close()

    return p_id

def enterTournament(t_id, p_id):
    """Adds a player and tournament to database.

    Args:
     t_id: tournament id of the tournament which player is being registered to.
     p_id: player id that is being registered
    """
    db = connect()
    cursor = db.cursor()
    query = "INSERT INTO registeredPlayers (t_id,p_id) VALUES (%s,%s);"
    cursor.execute(query, (t_id,p_id,))
    db.commit()
    db.close()

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
    db = connect()
    cursor = db.cursor()
    if t_id != None:
        query = "SELECT * FROM v_standings WHERE t_id = (%s)";
        cursor.execute(query, (t_id,))
    else:
        query = "SELECT * FROM v_standings;"
        cursor.execute(query)

    rows = cursor.fetchall()

    db.close()
    standings = []

    if t_id != None:
        for row in rows:
            standings.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
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

    db = connect()
    cursor = db.cursor()
    query = "INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (%s,%s,%s,%s,%s);"
    cursor.execute(query, (t_id, winner, loser, draw, bye, ))
    db.commit()
    db.close()

def checkBye(t_id, p_id):
    """Check if a player has a bye from standings 

    Args:
     t_id: tournament id 
     p_id: player id
    """
    db = connect()
    cursor = db.cursor()
    query = "SELECT byes FROM v_standings WHERE id = (%s) AND t_id = (%s);"
    cursor.execute(query, (t_id, p_id, ))
    row = cursor.fetchone()[0]
    db.close()

    if row == 0:
        return False

    return True

def checkMatches(t_id):
    """Return max matches played by everyone in standings 
    
    Args:
     t_id: tournament id 
    """
    db = connect()
    cursor = db.cursor()
    query = "SELECT max(matches) FROM v_standings WHERE t_id = (%s);"
    cursor.execute(query, (t_id, ))
    row = cursor.fetchone()[0]
    db.close()

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
            if checkBye(rows[i][1], rows[i][0]) == False and rows[i][5] < matchNum:
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
            if checkBye(rows[i][1], rows[i][0]) == False and rows[i][5] >= matchNum:
                rows.pop(i)
                numPlayers = numPlayers-1
                break   

    if t_id != None:
        for i in range(0,numPlayers-1,2):
            t = (rows[i][1],rows[i][2],rows[i+1][1],rows[i+1][2])
            temp.append(t)
    else:
        for i in range(0,numPlayers-1,2):
            t = (rows[i][0],rows[i][1],rows[i+1][0],rows[i+1][1])
            temp.append(t)


    return temp
