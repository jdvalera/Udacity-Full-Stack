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

CREATE TABLE tournaments (id SERIAL PRIMARY KEY, name TEXT);

CREATE TABLE matches (id SERIAL PRIMARY KEY,
                       t_id INTEGER REFERENCES tournaments (id),
					   winner INTEGER REFERENCES players (id),
					   loser INTEGER REFERENCES players (id),
                       draw BOOLEAN, bye BOOLEAN);


/*
CREATE TABLE results (tournament INTEGER REFERENCES tournaments (id),
                      player INTEGER REFERENCES players (id),
                      matches INTEGER REFERENCES matches (id),
                      score INTEGER);*/

CREATE TABLE registeredPlayers (t_id INTEGER REFERENCES tournaments (id),
                                p_id INTEGER REFERENCES players (id));

/* 
-- Wins View
-- Creates a view showing wins for each player
CREATE VIEW v_wins AS 
    SELECT registeredPlayers.t_id, foo.id, foo.name, foo.wins 
    FROM registeredPlayers, 
    	 (SELECT players.id, players.name, COUNT(matches.winner) AS wins 
         FROM players LEFT JOIN matches 
    	 ON players.id = matches.winner AND matches.draw != 't' GROUP BY players.id) AS foo
     WHERE registeredPlayers.p_id = foo.id ORDER BY t_id, wins DESC;

-- Draws View
-- Creates a view showing draws for each player
CREATE VIEW v_draws AS
    SELECT registeredPlayers.t_id, foo.id, foo.name, foo.draws 
    FROM registeredPlayers,
        (SELECT players.name, players.id, COUNT(matches.draw) AS draws
        FROM players LEFT JOIN matches
        ON (players.id = matches.winner OR players.id = matches.loser) AND matches.draw = 't' GROUP BY players.id) AS foo
    WHERE registeredPlayers.p_id = foo.id ORDER BY t_id, draws DESC;

-- Wins/Draws/Score View
-- Create a view showing wins/draws/score for each player.
-- Win = 3pts. Loss = 0pts. Draw = 1pt.
CREATE VIEW v_scores AS
    SELECT v_wins.t_id,v_wins.id,v_wins.name,v_wins.wins,v_draws.draws,(wins*3)+draws AS score 
    FROM v_wins,v_draws WHERE v_wins.id = v_draws.id ORDER BY t_id, score DESC;


-- Matches View
-- Creates a view showing all matches played by each player
CREATE VIEW v_matches AS 
    SELECT matches.t_id,players.id,players.name,count(matches) AS matches 
    FROM players left join matches ON winner=players.id OR loser=players.id GROUP BY matches.t_id, players.id, players.name;

-- Opponent Match Wins View
-- Uses the v_wins view along with the matches table unioned with itself to create a omw view
CREATE VIEW v_omw AS
SELECT t_id, id, name, wins, draws, score,  
    (
     SELECT SUM(wins) FROM v_scores, 
        -- Union gathers the players that v_scores.id has played
        (
         SELECT winner AS played FROM matches WHERE v_scores.id = matches.loser
         UNION
         SELECT loser AS played FROM matches  WHERE v_scores.id = matches.winner
        ) AS foo
     WHERE v_scores.id = foo.played
    ) AS omw
    --Needs to be from v_scores so v_scores.id can be used inside the union
FROM v_scores;

-- Opponent Match Score View
CREATE VIEW v_oms AS
SELECT t_id, id, name, wins, draws, score, 
    (
     SELECT SUM(score) FROM v_scores, 
        -- Union gathers the players that v_scors.id has played
        (
         SELECT winner AS played FROM matches WHERE v_scores.id = matches.loser
         UNION
         SELECT loser AS played FROM matches  WHERE v_scores.id = matches.winner
        ) AS foo
     WHERE v_scores.id = foo.played
    ) AS oms
    --Needs to be from v_wins so v_wins.id can be used inside the union
FROM v_scores;

-- Player standings ordered by wins and omw if there is a tie
-- Uses v_wins & v_matches to create a view that lists matches won and played for each player
CREATE VIEW v_standings AS 
    SELECT v_omw.id, v_omw.name, v_omw.wins, v_matches.matches, v_omw.omw
    FROM v_omw,v_matches WHERE v_omw.id = v_matches.id ORDER BY wins DESC, omw DESC;



--Shows all matches played (might need for no rematch)
 CREATE VIEW all_matches AS 
    SELECT v_standings.id, v_standings.name, matches.winner, matches.loser 
    FROM v_standings, matches WHERE v_standings.id = matches.winner OR v_standings.id = matches.loser;


-- Losses View
-- Creates a view showing losses for each player
CREATE VIEW v_losses AS 
    SELECT players.name, players.id, COUNT(matches.loser) AS losses 
    FROM players join matches ON players.id = matches.loser GROUP BY players.id;

*/


/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TESTING AREA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

INSERT INTO players (name) VALUES ('John');
INSERT INTO players (name) VALUES ('Amy');
INSERT INTO players (name) VALUES ('Jessica');
INSERT INTO players (name) VALUES ('Tom');
INSERT INTO players (name) VALUES ('Annie');
INSERT INTO players (name) VALUES ('Kate');
INSERT INTO players (name) VALUES ('Sheryl');
INSERT INTO players (name) VALUES ('Kathy');
INSERT INTO players (name) VALUES ('Nikki');

INSERT INTO tournaments (name) VALUES ('Tournament 1');

INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,1);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,2);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,3);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,4);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,5);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,6);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,7);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,8);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,9);


INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (1,1,2,'f','f');
INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (1,4,3,'f','f');
INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (1,5,6,'f','f');
INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (1,8,7,'t','f');
INSERT INTO matches (t_id, winner, draw, bye) VALUES (1,9,'f','t');

INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (1,1,4,'f','f');
INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (1,5,9,'f','f');
INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (1,2,3,'t','f');
INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (1,6,7,'f','f');
INSERT INTO matches (t_id, winner, draw, bye) VALUES (1,8,'f','t');

/*
CREATE VIEW played_temp AS SELECT id,name,winner as played 
 FROM (SELECT * FROM all_matches) AS foo1 union SELECT id,name,loser FROM (SELECT * FROM all_matches) AS foo;

CREATE VIEW played AS SELECT * FROM played_temp WHERE id != played;

CREATE VIEW played_standings AS SELECT played.id,played.name,played,wins,matches FROM played LEFT JOIN v_standings on played.id=v_standings.id;

*/

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
