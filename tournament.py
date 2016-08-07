#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect(database_name = "tournament2"):
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

    query = "INSERT INTO players (name, game, score, opscore) VALUES(%s,%s,%s,%s);"
    parameter = (name, n_game, 0, 0)
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
      A list of tuples,[(id, name, score, opsocre, wins, loses, draws),...,...]:
      sorted by score and opponants' score
    """
    cnn, cur = connect()
    query = """SELECT players.id, name, score, opscore FROM players
                WHERE game = %s ORDER BY score DESC, opscore DESC"""
                # [(7, 'jing', 213, 124), (20, 'joe', 134, 151)...]   game = n_game
    query_win_count = """SELECT COUNT(winner) FROM players LEFT JOIN matches ON
                         players.id = winner WHERE game = %s GROUP BY
                         players.id ORDER BY score DESC, opscore DESC"""
                # [(6,),(8,),(7,)...] group by id, sorted by score , game = n_game
    query_lose_count = """SELECT COUNT(loser) FROM players LEFT JOIN matches ON
                          players.id = loser WHERE game = %s GROUP BY players.id
                          ORDER BY score DESC, opscore DESC"""
                # [(6,),(8,),(7,)...] group by id, sorted by score , game = n_game

    query_draw_count_1 = """SELECT COUNT(draw1) FROM players LEFT JOIN matches ON
                            players.id = draw1 WHERE game = %s GROUP BY
                            players.id ORDER BY score DESC, opscore DESC"""
                # [(6,),(8,),(7,)...] group by id, sorted by score , game = n_game

    query_draw_count_2 = """SELECT COUNT(draw2) FROM players LEFT JOIN matches ON
                            players.id = draw2 WHERE game = %s GROUP BY
                            players.id ORDER BY score DESC, opscore DESC"""
                # [(6,),(8,),(7,)...] group by id, sorted by score , game = n_game
    parameter = (n_game,)
    try:
        # sorted by score first, then by opscore which is opponant's score
        cur.execute(query, parameter)
        result_player_state = cur.fetchall()

        cur.execute(query_win_count, parameter)
        result_win_count = cur.fetchall()

        cur.execute(query_lose_count, parameter)
        result_lose_count = cur.fetchall()

        cur.execute(query_draw_count_1,parameter)
        result_draw_count_1 = cur.fetchall()

        cur.execute(query_draw_count_2,parameter)
        result_draw_count_2 = cur.fetchall()

        result_draw_count = [tuple(sum(item) for item in zip(x,y)) for x,y
                             in zip(result_draw_count_1,result_draw_count_2)]

        result_list = [x+y+z+m for x,y,z,m in zip(result_player_state,
                       result_win_count, result_lose_count, result_draw_count)]
        return result_list
    except:
        print "<error5>"

def reportMatch(winner, loser, n_game, draw=False):
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
    query_match_report = """INSERT INTO matches (winner, loser, draw1, draw2)
                            VALUES (%s, %s, %s, %s)"""
    if draw == False:
        p_match = (winner, loser, None, None)
        query_winner_update = """UPDATE players SET score=score+3,
                                opscore=opscore+%s WHERE id = %s"""
        query_loser_update = """UPDATE players SET score=score+0,
                                opscore=opscore+%s+3 WHERE id = %s"""
    else:
        p_match = (None, None, winner, loser)
        query_winner_update = """UPDATE players SET score=score+1, opscore=opscore+%s+1 WHERE id=%s"""
        query_loser_update = """ UPDATE players SET score=score+1, opscore=opscore+%s+1 WHERE id=%s"""

    #get the current score of both winner and loser in order to use it to
    #update each other's opponant score.
    cur.execute("SELECT score FROM players WHERE id=%s",(winner,))
    w_score = cur.fetchone()[0]
    cur.execute("SELECT score FROM players WHERE id=%s",(loser,))
    l_score = cur.fetchone()[0]

    p_winner = (l_score, winner)
    p_loser = (w_score, loser)

    cur.execute(query_match_report, p_match)
    cur.execute(query_winner_update, p_winner)
    cur.execute(query_loser_update, p_loser)

    cnn.commit()
    cnn.close()

bye_list = [] # using bye_list to record who has already been matched with bye in this game.

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
    cnn, cur = connect()
    query = """SELECT id, name FROM players WHERE game=%s ORDER BY score DESC,
               opscore DESC"""
    parameter = (n_game,)
    cur.execute(query, parameter)
    tuple_list = cur.fetchall() # this list is already sorted by players' performance including their score so far and their opponants' score.
    if len(tuple_list)%2 == 0:
        # if there are an even number of players, then just add every the even position element with every odd position element one by one.
        result_list = [ x+y for x, y in zip(tuple_list[0::2],tuple_list[1::2])]
    else:
        # if we have an odd number of players, use while loop to find the last one who haven't matched with bye before.
        # and match them together and record this lucky player's id into bye_list. then break the loop.
        index = 0
        bye = (0, 'bye')
        while index < len(tuple_list):
            if tuple_list[-1-index][0] not in bye_list:
                tuple_list.remove(tuple_list[-1-index])
                result_list =  [x+y for x, y in zip(tuple_list[0::2], tuple_list[1::2])].append(tuple_list[-1-index]+bye)
                bye_list.append(tuple_list[-1-index][0])
                break
            index += 1
    return result_list
