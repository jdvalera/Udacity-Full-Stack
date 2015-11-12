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
-- COALESCE(foo.t_id, 0) is used to make t_id = 0 if t_id is Null 
-- (This is used in v_scores so v_wins.t_id = v_draws.t_id works)
CREATE VIEW v_wins AS 
        SELECT COALESCE(foo.t_id, 0) AS t_id, foo.id, foo.name, COUNT(matches.winner) AS wins 
        FROM (SELECT * FROM players LEFT JOIN registeredPlayers 
        ON players.id = registeredPlayers.p_id) AS foo LEFT JOIN matches 
    	ON foo.id = matches.winner AND matches.draw != 't' AND (matches.t_id is null OR matches.t_id = foo.t_id) 
        GROUP BY foo.t_id, foo.id, foo.name;


-- Draws View
-- Creates a view showing draws for each player
CREATE VIEW v_draws AS
    SELECT COALESCE(foo.t_id, 0) AS t_id, foo.id, foo.name, COUNT(matches.draw) AS draws
    FROM (SELECT * FROM players LEFT JOIN registeredPlayers 
    ON players.id = registeredPlayers.p_id) AS foo LEFT JOIN matches
    ON (foo.id = matches.winner OR foo.id = matches.loser) AND matches.draw = 't' 
    AND (matches.t_id is null OR matches.t_id = foo.t_id) GROUP BY foo.t_id, foo.id, foo.name;

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
    FROM (SELECT * FROM players LEFT JOIN registeredPlayers 
    ON players.id = registeredPlayers.p_id) AS foo 
    LEFT JOIN matches ON (winner=foo.id OR loser=foo.id) 
    AND matches.bye = 't' AND (matches.t_id is null OR matches.t_id = foo.t_id)
    GROUP BY foo.t_id, foo.id, foo.name;

-- Matches View
-- Creates a view showing all matches played by each player
CREATE VIEW v_matches AS 
    SELECT COALESCE(foo.t_id, 0) AS t_id,foo.id,foo.name,count(matches) AS matches 
    FROM (SELECT * FROM players LEFT JOIN registeredPlayers 
    ON players.id = registeredPlayers.p_id) AS foo 
    LEFT JOIN matches ON (winner=foo.id OR loser=foo.id) AND (matches.t_id is null OR matches.t_id = foo.t_id)
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


-- Player standings ordered by wins and oms if there is a tie
-- Uses v_oms, v_matches, v_byes to create a view that lists matches won and played for each player
CREATE VIEW v_standings AS 
    SELECT v_oms.t_id, v_oms.id, v_oms.name, v_oms.wins, v_oms.draws, v_matches.matches, v_oms.score, v_oms.oms, v_byes.byes
    FROM v_oms,v_matches,v_byes WHERE v_oms.id = v_matches.id AND v_oms.id = v_byes.id 
    AND v_oms.t_id = v_matches.t_id AND v_oms.t_id = v_byes.t_id
    ORDER BY t_id, wins DESC, oms DESC, id DESC;
