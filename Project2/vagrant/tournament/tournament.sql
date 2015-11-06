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

-- Creates a view showing wins for each player
CREATE VIEW v_wins as 
	 SELECT players.name, players.id, COUNT(matches.winner) AS 
	 wins FROM players left join matches 
	 on players.id = matches.winner GROUP BY players.id ORDER BY wins DESC;

CREATE VIEW v_losses AS 
	SELECT players.name, players.id, COUNT(matches.loser) AS 
	losses FROM players join matches on players.id = matches.loser GROUP BY players.id;

-- Creates a view showing all matches played by each player
CREATE VIEW v_matches AS SELECT players.id,count(matches) as
 matches FROM players left join matches on winner=players.id or loser=players.id GROUP BY players.id;

-- Uses v_wins & v_matches to create a view that lists matches won and played for each player
CREATE VIEW v_standings AS SELECT v_wins.id, v_wins.name, v_wins.wins, v_matches.matches
 FROM v_wins,v_matches WHERE v_wins.id = v_matches.id ORDER BY wins DESC;