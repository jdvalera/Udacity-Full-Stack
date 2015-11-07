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
	 SELECT players.name, players.id, COUNT(matches.winner) AS 
	 wins FROM players left join matches 
	 ON players.id = matches.winner GROUP BY players.id ORDER BY wins DESC;

-- Losses View
-- Creates a view showing losses for each player
CREATE VIEW v_losses AS 
	SELECT players.name, players.id, COUNT(matches.loser) AS 
	losses FROM players join matches ON players.id = matches.loser GROUP BY players.id;

-- Matches View
-- Creates a view showing all matches played by each player
CREATE VIEW v_matches AS 
    SELECT players.id,count(matches) AS
    matches FROM players left join matches ON winner=players.id OR loser=players.id GROUP BY players.id;

-- Opponent Match Wins View
-- Uses the v_wins view along with the matches table unioned with itself to create a omw view
CREATE VIEW v_omw AS
SELECT id, name, wins, 
    (
     SELECT SUM(wins) FROM v_wins, 
        -- Union gathers the players that v_wins.id has played
        (
         SELECT winner AS played FROM matches WHERE v_wins.id = matches.loser
         UNION
         SELECT loser AS played FROM matches  WHERE v_wins.id = matches.winner
        ) AS foo
     WHERE v_wins.id = foo.played
    ) AS omw
    --Needs to be from v_wins so v_wins.id can be used inside the union
FROM v_wins;

-- Player standings ordered by wins and omw if there is a tie
-- Uses v_wins & v_matches to create a view that lists matches won and played for each player
CREATE VIEW v_standings AS 
    SELECT v_omw.id, v_omw.name, v_omw.wins, v_matches.matches, v_omw.omw
    FROM v_omw,v_matches WHERE v_omw.id = v_matches.id ORDER BY wins DESC, omw DESC;



--Shows all matches played (might need for no rematch)
 CREATE VIEW all_matches AS 
    SELECT v_standings.id, v_standings.name, matches.winner, matches.loser 
    FROM v_standings, matches WHERE v_standings.id = matches.winner OR v_standings.id = matches.loser;


/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TESTING AREA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

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


CREATE VIEW played_temp AS SELECT id,name,winner as played 
 FROM (SELECT * FROM all_matches) AS foo1 union SELECT id,name,loser FROM (SELECT * FROM all_matches) AS foo;

CREATE VIEW played AS SELECT * FROM played_temp WHERE id != played;

CREATE VIEW played_standings AS SELECT played.id,played.name,played,wins,matches FROM played LEFT JOIN v_standings on played.id=v_standings.id;

/* Test to view who has played id=2
SELECT loser AS played FROM matches WHERE winner=2
UNION
SELECT winner FROM matches WHERE loser=2;
*/

 /* SELECT id,winner as played 
 FROM (SELECT * FROM all_matches where id=1) AS foo1 union SELECT id,loser FROM (SELECT * FROM all_matches where id=1) AS foo; */

 /* CREATE VIEW test3 AS SELECT id,winner as played 
 FROM (SELECT * FROM all_matches where id=1) AS foo1 union SELECT id,loser FROM (SELECT * FROM all_matches where id=1) AS foo;
*/

