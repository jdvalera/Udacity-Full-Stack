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
    query = "DELETE from matches";
    cursor.execute(query)
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    cursor = db.cursor()
    query = "DELETE from players";
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


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    cursor = db.cursor()
    query = "INSERT INTO players (name) VALUES (%s);"
    cursor.execute(query, (name, ))
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    cursor = db.cursor()
    query = "SELECT * FROM v_standings";
    cursor.execute(query)
    rows = cursor.fetchall()
    db.close()
    standings = []
    for row in rows:
        standings.append((row[0],row[1],row[2],row[3]))
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    #INSERT INTO matches (winner, loser) VALUES (1,2);
    db = connect()
    cursor = db.cursor()
    query = "INSERT INTO matches (winner, loser) VALUES (%s,%s);"
    cursor.execute(query, (winner, loser, ))
    db.commit()
    db.close()
 
 
def swissPairings():
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
    rows = playerStandings()
    temp = []
    for i in range(0,countPlayers()-1,2):
        t = (rows[i][0],rows[i][1],rows[i+1][0],rows[i+1][1])
        temp.append(t)
    return temp

#registerPlayer('John')
#print countPlayers()
#s = playerStandings()
#print s[0]
#reportMatch(15,16)
#s = swissPairings()
#print s[0]
#print s[1]
