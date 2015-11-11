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

CREATE TABLE registeredPlayers (t_id INTEGER REFERENCES tournaments (id),
                                p_id INTEGER REFERENCES players (id));


-- Wins View
-- Creates a view showing wins for each player
CREATE VIEW v_wins AS 
        SELECT COALESCE(foo.t_id, 0) AS t_id, foo.id, foo.name, COUNT(matches.winner) AS wins 
        FROM (SELECT * FROM players LEFT JOIN registeredPlayers ON players.id = registeredPlayers.p_id) AS foo LEFT JOIN matches 
    	ON foo.id = matches.winner AND matches.draw != 't' AND matches.t_id = foo.t_id GROUP BY foo.t_id, foo.id, foo.name;


-- Draws View
-- Creates a view showing draws for each player
CREATE VIEW v_draws AS
    SELECT COALESCE(foo.t_id, 0) AS t_id, foo.id, foo.name, COUNT(matches.draw) AS draws
    FROM (SELECT * FROM players LEFT JOIN registeredPlayers ON players.id = registeredPlayers.p_id) AS foo LEFT JOIN matches
    ON (foo.id = matches.winner OR foo.id = matches.loser) AND matches.draw = 't' AND matches.t_id = foo.t_id GROUP BY foo.t_id, foo.id, foo.name;

-- Wins/Draws/Score View
-- Create a view showing wins/draws/score for each player.
-- Win = 3pts. Loss = 0pts. Draw = 1pt.
CREATE VIEW v_scores AS
    SELECT v_wins.t_id,v_wins.id,v_wins.name,v_wins.wins,v_draws.draws,(wins*3)+draws AS score 
    FROM v_wins,v_draws WHERE v_wins.id = v_draws.id AND v_wins.t_id = v_draws.t_id
    ORDER BY t_id, score DESC;

-- Byes View
-- Create a view showing if a player has had a bye
CREATE VIEW v_byes AS 
    SELECT COALESCE(foo.t_id, 0) AS t_id, foo.id,foo.name,count(bye) AS byes
    FROM (SELECT * FROM players LEFT JOIN registeredPlayers ON players.id = registeredPlayers.p_id) AS foo 
    LEFT JOIN matches ON (winner=foo.id OR loser=foo.id) AND matches.bye = 't' AND matches.t_id = foo.t_id
    GROUP BY foo.t_id, foo.id, foo.name;

-- Matches View
-- Creates a view showing all matches played by each player
CREATE VIEW v_matches AS 
    SELECT COALESCE(foo.t_id, 0) AS t_id,foo.id,foo.name,count(matches) AS matches 
    FROM (SELECT * FROM players LEFT JOIN registeredPlayers ON players.id = registeredPlayers.p_id) AS foo 
    LEFT JOIN matches ON (winner=foo.id OR loser=foo.id) AND matches.t_id = foo.t_id
    GROUP BY foo.t_id, foo.id, foo.name;

-- Opponent Match Wins View
-- Uses the v_scores view along with the matches table unioned with itself to create a omw view
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
-- Uses the v_scores view along with the matches table unioned with itself to create a oms view
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
    --Needs to be from v_scores so v_scores.id can be used inside the union
FROM v_scores;


-- Player standings ordered by wins and omw if there is a tie
-- Uses v_omw, v_matches, v_byes to create a view that lists matches won and played for each player
CREATE VIEW v_standings AS 
    SELECT v_oms.t_id, v_oms.id, v_oms.name, v_oms.wins, v_oms.draws, v_matches.matches, v_oms.score, v_oms.oms, v_byes.byes
    FROM v_oms,v_matches,v_byes WHERE v_oms.id = v_matches.id AND v_oms.id = v_byes.id  AND v_oms.t_id = v_matches.t_id AND v_oms.t_id = v_byes.t_id
    ORDER BY t_id, wins DESC, oms DESC, id DESC;


/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TESTING AREA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

/*

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

/*
INSERT INTO players (name) VALUES ('John');
INSERT INTO players (name) VALUES ('Amy');
INSERT INTO players (name) VALUES ('Jessica');
INSERT INTO players (name) VALUES ('Tom');
INSERT INTO players (name) VALUES ('Annie');
INSERT INTO players (name) VALUES ('Kate');
INSERT INTO players (name) VALUES ('Sheryl');
INSERT INTO players (name) VALUES ('Kathy');
INSERT INTO players (name) VALUES ('Nikki');

INSERT INTO players (name) VALUES ('Aaron');
INSERT INTO players (name) VALUES ('Dicky');
INSERT INTO players (name) VALUES ('Kira');
INSERT INTO players (name) VALUES ('Namaste');

INSERT INTO tournaments (name) VALUES ('Tournament 1');
INSERT INTO tournaments (name) VALUES ('Tournament 2');

INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,1);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,2);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,3);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,4);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,5);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,6);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,7);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,8);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (1,9);

INSERT INTO registeredPlayers (t_id, p_id) VALUES (2,10);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (2,11);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (2,12);
INSERT INTO registeredPlayers (t_id, p_id) VALUES (2,13);

INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (2,10,11,'f','f');
INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (2,12,13,'f','f');

INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (2,10,12,'f','f');
INSERT INTO matches (t_id, winner, loser, draw, bye) VALUES (2,11,13,'f','f');


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
*/

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
