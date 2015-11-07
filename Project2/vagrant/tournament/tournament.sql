-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE tournament;
CREATE DATABASE tournament;
\c tournament;

CREATE TABLE players( id SERIAL PRIMARY KEY, name TEXT);

CREATE TABLE matches (id SERIAL PRIMARY KEY,
					   winner INTEGER REFERENCES players (id),
					   loser INTEGER REFERENCES players (id));


-- Wins View
-- Creates a view showing wins for each player
CREATE VIEW v_wins AS
	 SELECT players.name, players.id, COUNT(matches.winner) AS wins 
     FROM players LEFT JOIN matches 
	 ON players.id = matches.winner GROUP BY players.id ORDER BY wins DESC;

-- Losses View
-- Creates a view showing losses for each player
CREATE VIEW v_losses AS 
	SELECT players.name, players.id, COUNT(matches.loser) AS losses 
    FROM players join matches ON players.id = matches.loser GROUP BY players.id;

-- Matches played View
-- Creates a view showing all matches played by each player
CREATE VIEW v_matches AS 
    SELECT players.id,count(matches) AS matches 
    FROM players LEFT JOIN matches ON winner=players.id OR loser=players.id GROUP BY players.id;

-- Player standings ordered by wins
-- Uses v_wins & v_matches to create a view that lists matches won and played for each player
CREATE VIEW v_standings AS 
    SELECT v_wins.id, v_wins.name, v_wins.wins, v_matches.matches
    FROM v_wins,v_matches WHERE v_wins.id = v_matches.id ORDER BY wins DESC;


 /*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TESTING AREA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

INSERT INTO players (name) VALUES ('John');
INSERT INTO players (name) VALUES ('Amy');
INSERT INTO players (name) VALUES ('Jessica');
INSERT INTO players (name) VALUES ('Tom');
INSERT INTO players (name) VALUES ('Annie');
INSERT INTO players (name) VALUES ('Kate');
INSERT INTO players (name) VALUES ('Sheryl');
INSERT INTO players (name) VALUES ('Kathy');

INSERT INTO matches (winner, loser) VALUES (1,2);
INSERT INTO matches (winner, loser) VALUES (4,3);
INSERT INTO matches (winner, loser) VALUES (5,6);
INSERT INTO matches (winner, loser) VALUES (8,7);

INSERT INTO matches (winner, loser) VALUES (1,4);
INSERT INTO matches (winner, loser) VALUES (5,8);
INSERT INTO matches (winner, loser) VALUES (3,6);
INSERT INTO matches (winner, loser) VALUES (2,7);
