#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
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

def playerStandings(t_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (t_id, p_id, name, wins, draws, score, omw, matches, bye):
        t_id: the id of the tournament the players are registered to
        p_id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        draws: the number of draws the player has
        score: the player's score (win=3,lose=0,draw=1)
        oms: Opponent Match Score (collective score of each opponent that the player has played)
        matches: the number of matches the player has played
        byes: if the player has had a bye 
    """
    db = connect()
    cursor = db.cursor()
    query = "SELECT * FROM v_standings WHERE t_id = (%s)";
    cursor.execute(query, (t_id,))
    rows = cursor.fetchall()
    db.close()
    standings = []
    for row in rows:
        standings.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
    return standings


def reportMatch(winner, t_id=1, loser=None, draw=False, bye=False):
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
    """Check if a player has a bye from standings """
    db = connect()
    cursor = db.cursor()
    query = "SELECT byes FROM v_standings WHERE id = (%s) AND t_id = (%s);"
    cursor.execute(query, (t_id, p_id, ))
    row = cursor.fetchall()
    db.close()

    if row[0][0] == 0:
        return True

    return False

 
 
def swissPairings(t_id):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    rows = playerStandings(t_id)
    temp = []
    numPlayers = countTournamentPlayers(t_id)

    if numPlayers%2 != 0:
        for i in range(numPlayers, 0, -1):
            if checkBye(rows[i][0], rows[i][1]) == False:
                reportMatch(rows[i][1], rows[i][0])
                rows.pop(i)
                numPlayers = numPlayers-1
                break
    
    for i in range(0,numPlayers-1,2):
        t = (rows[i][0],rows[i][1],rows[i+1][0],rows[i+1][1])
        temp.append(t)
    return temp

#standings = playerStandings(2)
#print standings[0]
#[(t_id1, p_id1, name1, wins1, draws1, score1, oms1, matches1, byes1), (t_id2, p_id2, name2, wins2, draws2, score2, oms2, matches2, byes2)] = standings
#print t_id1, p_id1, name1, wins1, draws1, score1, oms1, matches1, byes1
#[id1, id2, id3, id4] = [row[1] for row in standings]
#print [row[1] for row in standings]
#print checkBye(1,1)[0][0] == 0
#print countPlayers()
#print countTournamentPlayers(2)
#print countTournamentPlayers(1)
#print registerPlayer("Jorge")
#print createTournament("Tournament 3")