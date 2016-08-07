-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
CREATE TABLE players
(
  id SERIAL PRIMARY KEY,
  name TEXT,
  game INTEGER NOT NULL,
  score INTEGER NOT NULL,
  opscore INTEGER NOT NULL
);

CREATE TABLE matches
(
  id SERIAL PRIMARY KEY,
  winner INTEGER REFERENCES players(id),
  loser INTEGER REFERENCES players(id),
  draw1 INTEGER REFERENCES players(id),
  draw2 INTEGER REFERENCES players(id)
)
