-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP VIEW IF EXISTS player_opscore;
DROP VIEW IF EXISTS op_list;
DROP VIEW IF EXISTS player_score;
DROP VIEW IF EXISTS player_state;
DROP VIEW IF EXISTS win_count;
DROP VIEW IF EXISTS lost_count;
DROP VIEW IF EXISTS draw_count;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;

CREATE TABLE players
(
  id SERIAL PRIMARY KEY,
  name TEXT,
  game INTEGER NOT NULL
);

CREATE TABLE matches
(
  id SERIAL PRIMARY KEY,
  winner INTEGER REFERENCES players(id),
  loser INTEGER,
  draw BOOLEAN NOT NULL
);

CREATE or replace VIEW op_list AS
SELECT p.id, loser AS op FROM players p JOIN matches ON p.id = winner
UNION
SELECT p.id, winner AS op FROM players p JOIN matches ON p.id = loser;

CREATE VIEW win_count AS
SELECT p.id, COUNT(winner) FROM players p LEFT JOIN matches m
ON p.id=winner AND draw=False
GROUP BY p.id ORDER BY p.id;

CREATE VIEW lost_count AS
SELECT p.id, COUNT(loser) FROM players p LEFT JOIN matches
ON p.id=loser AND draw=False
GROUP BY p.id ORDER BY p.id;

CREATE VIEW draw_count AS
SELECT p.id, count(m.id) FROM players p LEFT JOIN matches m
ON (p.id=winner or p.id = loser) AND draw=True
GROUP BY p.id ORDER BY p.id;

CREATE VIEW player_state AS
SELECT w.id, w.count AS wins,l.count AS losts, d.count AS draws
FROM win_count w
JOIN lost_count l
  ON w.id = l.id
JOIN draw_count d
  ON l.id = d.id;

CREATE VIEW player_score AS
SELECT id, wins*3+draws AS score FROM player_state;

CREATE VIEW player_opscore AS
SELECT player_score.id, SUM(score) AS opscore
FROM op_list RIGHT JOIN player_score ON op=player_score.id GROUP BY player_score.id;
