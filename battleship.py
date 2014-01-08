#!/usr/bin/env python -tt

import re
import os
import math
import time
import string
import logging
import argparse
from random import choice
from random import randint

##------- initialize game variables --------##
board = []
ship_board =[]
ship_locations = []
column_headers = list(string.ascii_uppercase)

##---------- customizable options ----------##
ships = [2,3,4,3,5]
num_turns = 10
difficulty = {'EASY':2.3,'MEDIUM':2.5,'HARD':2.8}

##---------- config parameters -------------##

parser = argparse.ArgumentParser(description='Battleship game! by Brian Babbitt')

parser.add_argument('-v','--verbose', action='store_true', default=0, help='Change the level of logging')
parser.add_argument('-d','--difficulty', choices=['easy','medium','hard'], help='Set difficulty level, default is medium')
parser.add_argument('-m','--mode', choices=['PVE','PVP'], help='Set game mode')

args = parser.parse_args()

if args.verbose is True:
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
else:
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

##---------- pick random coords ------------##
def random_row(board):
  return randint(0, len(board) - 1)

def random_col(board):
  return randint(0, len(board[0]) - 1)

##----- convert column number to letter ----##
def base_26_converter(column):
  column = float(column)
  answer = ""
  list_of_remainders = []
  if column > 26:
    while column > 26:
      if (column%26) == 0.0:
        list_of_remainders.append((column%26))
        column = int(math.floor(column/26)-1)
      else:
        list_of_remainders.append(column%26)
        column = int(math.floor(column/26))
  
  list_of_remainders.append(column)
  list_of_remainders.reverse()
  
  for column in list_of_remainders:
    answer = answer + str(column_headers[int(column)-1])
  return answer

##------ determine size of board -----------##
def create_blank_game_board(level=difficulty['MEDIUM']):
  board_size = int(math.pow(max(ships),level)) ## start at max ship size
  logging.debug('Starting number of squares on board is: {}'.format(board_size))
  logging.debug('Starting number of ship segments is: {}'.format(sum(ships)))
  
  while board_size < sum(ships)*2:
    logging.debug('Board size is to small: {}'.format(board_size))
    board_size+=1
  
  logging.debug('Final number of squares on board is: {}'.format(board_size))
  board_size = int(board_size**(.5))
  logging.debug('Final board length is: {}'.format(board_size))
  
  for x in range(board_size):
    board.append(["O"] * board_size)
    ship_board.append(["0"] * board_size)

##---------- print game board --------------##
def print_board(board):
  i = 0
  print '\n   ',
  for column in range(len(board)):
    i+=1
    print base_26_converter(i),
  print ''
  print '___'+('__'*i)
  i = 1
  for row in board:
    print "{} |".format(i),
    print " ".join(row)
    i+=1
  print '\n'

##------- check ship placement -------------##
def check_ship(guess_row, guess_col):
  logging.debug('Checking if ship present at {},{}'.format(guess_row, guess_col))
  for x in range(len(ship_locations)):
    for y in ship_locations[x]:
      if ship_locations[x][y] == [guess_row, guess_col]:
        logging.debug('Ship is already present at this location ({},{})'.format(guess_row, guess_col))
        return True
  
  logging.debug('Location is available ({},{})'.format(guess_row, guess_col))
  return False

##----------- auto place ship --------------##
def auto_place_ship(ship_size, ship_number):
  logging.debug('Stats for ship #{} - ship size: {}'.format(ship_number+1, ship_size))
  start = time.clock()
  ship_segments = ship_size
  ship_locations.append({})
  loop_count = 0
  loop_count2 = 0
  
  while ship_segments != 0:
    logging.debug('Number of remaining segments to place: {}'.format(ship_segments))
    
    ## first segment sets starting point
    if ship_segments == ship_size:
      temp_row = random_row(board)
      temp_col = random_col(board)
      if check_ship(temp_row, temp_col) is False:
        ship_locations[ship_number][0] = [temp_row,temp_col]
        ship_segments -= 1
      else:
        logging.debug('Will attempt to pick different coords for ship.')
        continue
    
    ## second segment determines orientation
    elif ship_segments == (ship_size - 1):
      logging.debug('Placing second segment, determining orientation')
      
      temp_point = choice([{'dir':'row','loc':temp_row-1},{'dir':'row','loc':temp_row+1},{'dir':'col','loc':temp_col-1},{'dir':'col','loc':temp_col+1}])
      logging.debug('Random direction and new location: {} {}'.format(temp_point['dir'],temp_point['loc']))
      logging.debug('Checking if coords are on board...')
      if temp_point['loc'] >= 0 and temp_point['loc'] < len(board):
        logging.debug('Coords are valid on board')
        if temp_point['dir'] == 'col':
          temp_col2 = temp_point['loc']
          temp_row2 = temp_row
          direction = 'horizontal'
        else:
          temp_row2 = temp_point['loc']
          temp_col2 = temp_col
          direction = 'vertical'
        
        if check_ship(temp_row2, temp_col2) is False:
          ship_locations[ship_number][1] = [temp_row2, temp_col2]
          ship_segments -= 1
          logging.debug('Ships orientation is {}'.format(direction))
        elif check_ship(temp_row2, temp_col2) is True:
          loop_count2 += 1
          logging.debug('Attempting to retry segment assignment: {}'.format(loop_count2))
          if loop_count2 == 8:
            ship_segments = ship_size
            loop_count2 = 0
            logging.debug('Will reset and pick new coords for ship.')
            ship_locations[ship_number].clear()
            continue
          continue
      else:
        logging.debug('Coords are NOT valid on board')
        continue
    
    ## all other subsequent segments
    else:
      if direction == 'horizontal':
        logging.debug('temp_col2: {} temp_col: {}'.format(temp_col2,temp_col))
        if temp_col2 > temp_col:
          temp_point = choice([{'dir':'col','loc':temp_col2+1},{'dir':'col','loc':temp_col-1}])
        else:
          temp_point = choice([{'dir':'col','loc':temp_col2-1},{'dir':'col','loc':temp_col+1}])
        logging.debug('temp_point: {}'.format(temp_point))
      if direction == 'vertical':
        logging.debug('temp_row2: {} temp_row: {}'.format(temp_row2,temp_row))
        if temp_row2 > temp_row:
          temp_point = choice([{'dir':'row','loc':temp_row2+1},{'dir':'row','loc':temp_row-1}])
        else:
          temp_point = choice([{'dir':'row','loc':temp_row2-1},{'dir':'row','loc':temp_row+1}])
        logging.debug('temp_point: {}'.format(temp_point))
      if temp_point['loc'] >= 0 and temp_point['loc'] < len(board):
        if temp_point['dir'] == 'col':
          temp_col3 = temp_point['loc']
          temp_row3 = temp_row2
        else:
          temp_row3 = temp_point['loc']
          temp_col3 = temp_col2
        if check_ship(temp_row3, temp_col3) is False:
          ship_locations[ship_number][len(ship_locations[ship_number])] = [temp_row3, temp_col3]
          temp_col2 = temp_col3
          temp_row2 = temp_row3
          ship_segments -= 1
        elif check_ship(temp_row3, temp_col3) is True:
          loop_count += 1
          logging.debug('Attempting to retry segment assignment: {}'.format(loop_count))
          if loop_count == 8:
            ship_segments = ship_size
            loop_count = 0
            logging.debug('Will reset and pick new coords for ship.')
            ship_locations[ship_number].clear()
            continue
          continue
      else:
        logging.debug('Coords are NOT valid on board')
        continue
  
  logging.debug('Finished placing ship: {}'.format(ship_locations[ship_number]))
  logging.debug('Time to place ship: {}ms'.format((time.clock() - start)*1000))

##---------- check ship health -------------##
def check_ship_health(guess_row, guess_col):
  logging.debug('The ship hit has {} segments left'.format(ships[int(ship_board[guess_row][guess_col])-1]))
  ships[int(ship_board[guess_row][guess_col])-1] -= 1
  if ships[int(ship_board[guess_row][guess_col])-1] == 0:
    print 'You\'ve sunk my battleship!'
    if sum(ships) == 0:
      print 'You\'ve won! All battleships are destroyed!\n'
      print_board(ship_board)
      exit()

##------ input coords and validate ---------##
def input_coords():
  global guess_row, guess_col
  while True:
    try:
      user_input = raw_input('Enter row and column: ')
      p = re.compile('([0-9]*)([a-zA-Z]*)')
      m = p.match(user_input)
      group = m.groups()
      guess_row = group[0]
      guess_col = group[1]
      
      if guess_row.isdigit() is False or guess_col.isalpha() is False:
        print 'Invalid row or column. For example enter 4C'
        continue
      else:
        guess_row = int(guess_row)-1
        guess_col = int(column_headers.index(guess_col.upper()))
    except ValueError:
      print 'Invalid row or column. For example enter 4C'
      continue
    
    if guess_row >= 0 and guess_row <= len(board):
      if guess_col >= 0 and guess_col <= len(board):
        logging.debug('Coords are valid on game board')
        return False
      else:
        print 'Column is not on board'
        continue
    else:
      print 'Row is not on board'
      continue

##------------------------------------------##
def play_game():
  global num_turns, guess_row, guess_col
  create_blank_game_board(difficulty[game_level])
  
  logging.debug('There are a total of {} ships'.format(len(ships)))
  start = time.clock()
  
  ##---- place all ships and map to board ----##
  for x in range(len(ships)):
     logging.debug("{} out of {} ships have been placed".format(x,len(ships)))
     auto_place_ship(ships[x],x)
     
     for y in range(len(ship_locations[x])):
      ship_board[ship_locations[x][y][0]][ship_locations[x][y][1]] = str(x+1)
  
  logging.debug('Time to place all ships: {}ms'.format((time.clock() - start)*1000))
  #print_board(ship_board) ##--- CHEATING! Prints game board with ship locations ----##
  
  print "\nLet's play Battleship!\n"
  print_board(board)
  
  while num_turns != 0:
    
    ship_hit = None
    print "\n{} remaining turns \n".format(num_turns)
    
    input_coords()
    
    if(board[guess_row][guess_col] == 'X' or board[guess_row][guess_col] == '*' ):
      print "\nYou guessed that one already."
      ship_hit = False
    
    else:
      for x in range(len(ship_locations)):
        if [guess_row, guess_col] in ship_locations[x].values():
          print '\nHit!'
          check_ship_health(guess_row, guess_col)
          board[guess_row][guess_col] = "*"
          ship_hit = True
          break
    
    if ship_hit is None:
      print '\nMiss!'
      board[guess_row][guess_col] = "X"
      num_turns -= 1
    
    print_board(board)
  
  print 'Game Over\n'
  print 'Here\'s where all the ships were\n'
  print_board(ship_board)

##------------------------------------------##
def menu():
  global game_level, game_mode
  
  print '\nWelcome to Battleship!\n'
  
  if args.mode is None:
    print 'Select game mode:\n'
    print 'PVP - Player vs. Player'
    print 'PVE - Player vs. Environment/Computer'
    game_mode = raw_input('> ').upper()
  else:
    game_mode = args.mode.upper()
  
  if game_mode == 'PVE':
    if args.difficulty is None:
      game_level = raw_input('\nWhat level do you want to play (easy, medium or hard)? ').upper()
    else:
      game_level = args.difficulty.upper()
    play_game()
  
  elif game_mode == 'PVP':
    print 'PVP mode'
    pass


menu()

##------------- to do list ----------------------##
## allow player to place ships