#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect(database_name = "tournament4"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        cnn = psycopg2.connect("dbname={}".format(database_name))
        cur = cnn.cursor()
        return cnn, cur
    except:
        print "<error1, unable to connect>"

def deleteMatches():
    """Remove all the match records from the database."""
    cnn, cur = connect()
    query = "DELETE FROM matches;"
    try:
        cur.execute(query)
        cnn.commit()
    except:
        print "<error2, unable to delete matches>"
    cnn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    cnn, cur = connect()
    deleteMatches()
    query = """DELETE FROM players;"""
    try:
        cur.execute(query)
        cnn.commit()
    except:
        print "<error3, unable to delete players>"
    cnn.close()

def countPlayers(n_game=0):
    """Returns the number of players currently registered."""
    cnn, cur = connect()
    query = "SELECT COUNT(*) FROM players"
    query_n_game = "SELECT COUNT(*) FROM players WHERE game=%s"
    parameter = (n_game,)
    try:
        if n_game == 0:
            cur.execute(query)
        else:
            cur.execute(query_n_game, parameter)
    except:
        print "<error4>"
    result_list = cur.fetchone()
    cnn.close()
    return result_list[0]


def registerPlayer(name,n_game):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    cnn, cur = connect()
    query = "INSERT INTO players (name, game) VALUES(%s,%s);"
    parameter = (name, n_game)
    try:
        cur.execute(query, parameter)
        cnn.commit()
    except:
        print "<error5>"
    cnn.close()


def playerStandings(n_game):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples,[(id, name, score, opscore, wins, losts, draws),...,...]:
      sorted by score and opponants' score
    """
    cnn, cur = connect()
    query = """SELECT p.id, name, score, opscore, pst.wins, pst.losts, pst.draws
               FROM players p JOIN player_state ps ON p.id = ps.id
               LEFT JOIN player_score psc ON p.id = psc.id
               LEFT JOIN player_state pst ON p.id = pst.id
               LEFT JOIN player_opscore pop ON p.id = pop.id WHERE game = %s
               ORDER BY score DESC, opscore DESC;"""
    parameter = (n_game,)
    try:
        cur.execute(query, parameter)
        result_list = cur.fetchall()
        return result_list
    except:
        print "<error6>"
    cnn.close()

def reportMatch(winner, loser, draw=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost

    Score rules:
        win: get 3 points
        lose: get 0 points
        draw: get 1 points
        each round add the opponant's score to each other(used to sort when there is a tie)
    """
    cnn, cur = connect()
    query = """INSERT INTO matches (winner, loser, draw) VALUES (%s, %s, %s)"""
    parameter = (winner, loser, draw)
    try:
        cur.execute(query, parameter)
    except:
        print "<error7>"
    cnn.commit()
    cnn.close()

# using bye_list to record who has already been matched with bye in this game.
bye_list = []

def swissPairings(n_game):
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
    # the list return from standings
    list_1 = playerStandings(n_game)
    # only remain the id, name of those tuples in list_1
    list_2 = [x[0:2] for x in list_1]
    if len(list_2)%2 == 0:
        # if there are an even number of players, just match them one by one
        result_list = [ x+y for x, y in zip(list_2[0::2],list_2[1::2])]
    else:
        # if there are an odd number of players, match them with a bye
        index = 0
        bye = (0, 'bye')
        while index < len(list_2):
            # search from the last one if he/she has been matched with bye.
            if list_2[-1-index][0] not in bye_list:
                list_2.remove(list_2[-1-index])
                result_list =  [x+y for x, y in zip(list_2[0::2], list_2[1::2])]
                result_list.append(list_2[-1-index]+bye)
                bye_list.append(list_2[-1-index][0])
                break
            index += 1
    return result_list
