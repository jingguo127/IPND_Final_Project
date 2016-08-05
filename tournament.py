#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        cnn = psycopg2.connect("dbname=tournament")
        return cnn
    except:
        print "I am unable to connect to the database"

def deleteMatches():
    """Remove all the match records from the database."""
    cnn = connect()
    cur = cnn.cursor()
    query_string = """UPDATE games SET win=0, draw=0, matches=0, opscore=0, score=0"""
    try:
        cur.execute(query_string)
        cnn.commit()
    except:
        print "you query sucks"
    cnn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    cnn = connect()
    cur = cnn.cursor()
    query_string = """DELETE FROM users"""
    try:
        cur.execute("""DELETE FROM games""")
        cur.execute(query_string)
        cnn.commit()
    except:
        print "you query sucks again"
    cnn.close()

def countPlayers():
    """Returns the number of players currently registered."""
    cnn = connect()
    cur = cnn.cursor()
    query_string = """SELECT COUNT(*) FROM users"""
    try:
        cur.execute(query_string)
    except:
        print "wrong"
    l = cur.fetchall()
    cnn.close()
    return l[0][0]
    

def registerPlayer(name,n_game):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """    
    cnn = connect()
    cur = cnn.cursor()
    try:
        cur.execute("""INSERT INTO users(name) VALUES(%s)""",(name,))
        cur.execute("""SELECT ID FROM users WHERE name=%s""",(name,))
        id_user = cur.fetchall()
        id_game = id_user[-1][0]
        cur.execute("""INSERT INTO games VALUES(%s,%s,0,0,0,0,0)""",(id_game,n_game))
        cnn.commit()
    except:
        print "wrong2"
    cnn.close()


def playerStandings(n_game):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    cnn = connect()
    cur = cnn.cursor()
    try:
        # sorted by score first, then by opscore which is opponant's score
        cur.execute("""SELECT games.id, name, win, draw, matches, opscore, score FROM users JOIN games ON users.id=games.id WHERE game=%s ORDER BY score DESC, opscore DESC;""" ,(n_game,))
        result_list = cur.fetchall()
        return result_list
    except:
        print "wrong3"

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
    cnn = connect()
    cur = cnn.cursor()
    try:
        cur.execute("""SELECT win, draw, matches, opscore, score FROM games WHERE id=%s and game=%s;""",(winner, n_game))
        winner_former_state = cur.fetchall()
        cur.execute("""SELECT win, draw, matches, opscore, score FROM games WHERE id=%s and game=%s;""",(loser, n_game))
        loser_former_state = cur.fetchall()
    except:
        print "wrong4"
    if loser == 0:
        # the winner matched a 'bye'
        win_add = (0, 1, 1, loser_former_state[-1], 1)
        winner_update = tuple(sum(item) for item in zip(winner_former_state[0], win_add))+(winner, n_game)
        try:
            cur.execute("""UPDATE games SET win=%s, draw=%s, matches=%s, opscore=%s, score=%s WHERE id=%s and game=%s;""", winner_update)
            cnn.commit()   
        except:
            print "wrong5"
    else:
        if draw==False: # if it's not a draw, winner get 3 points and loser get 0 points. each of them add other's score to their opponant score.
            win_add = (1, 0, 1, loser_former_state[0][-1], 3)
            lose_add = (0, 0, 1, winner_former_state[0][-1], 0)
        else: # if it's a draw,  everyone get 1 points. each of them add other's score to their opponant score.
            win_add = (0, 1, 1, loser_former_state[-1], 1)
            lose_add = (0, 1, 1, winner_former_state[-1], 1)
        try:
            winner_update = tuple(sum(item) for item in zip(winner_former_state[0], win_add))+(winner, n_game)
            loser_update = tuple(sum(item) for item in zip(loser_former_state[0], lose_add))+(loser, n_game)
            cur.execute("""UPDATE games SET win=%s, draw=%s, matches=%s, opscore=%s, score=%s WHERE id=%s and game=%s;""", winner_update)
            cur.execute("""UPDATE games SET win=%s, draw=%s, matches=%s, opscore=%s, score=%s WHERE id=%s and game=%s;""", loser_update)
            cnn.commit()
        except:
            print "wrong6"
    cnn.close()




 
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
    cnn = connect()
    cur = cnn.sursor()
    bye_list = [] # using bye_list to record who has already been matched with bye in this game.
    bye = (0, 'bye')
    index = 0

    cur.execute("""SELECT games.id, name FROM users JOIN games ON id WHERE game=%s ORDER BY score, opscore""",(n_game,)) 
    tuple_list = cur.fetchall() # this list is already sorted by players' performance including their score so far and their opponants' score.
    if len(tuple_list)/2 == 0:
        # if there are an even number of players, then just add every the even position element with every odd position element one by one.
        result_list = [ x+y for x, y in zip(tuple_list[0::2],tuple_list[1::2])]
    else:
        # if we have an odd number of players, use while loop to find the last one who haven't matched with bye before.
        # and match them together and record this lucky player's id into bye_list. then break the loop.
        while index < len(tuple_list):
            if tuple_list[-1-index][0] not in bye_list:
                tuple_list.remove(tuple_list[-1-index])
                result_list =  [x+y for x, y in zip(tuple_list[0::2], tuple_list[1::2])].append(tuple_list[-1-index]+bye)
                bye_list.append(tuple_list[-1-index][0])
                break
            index += 1
    return result_list



