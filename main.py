from PIL import Image
import pytesseract
import numpy as np
import re
import sys
import pokebase as pb
import math
import nature
import argparse

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("file", type=str, help="The filepath to a stats screenshot from Pokemon Scarlet/Violet")
  parser.add_argument("-p", "--pokemon", help="Specify the pokemon being scanned.",
                    type=str)
  parser.add_argument("-v", "--verbosity", action="store_true",
                    help="Display full scanned OCR values.")                
  args = parser.parse_args()                  
  file = args.file
  
  img = np.array(Image.open(file))
  text = pytesseract.image_to_string(img)

  if(args.verbosity):
    print('=====IMAGE=====')
    print(text)
  pokemon = parse_ocr_output(text)
  nature_modified_stats = nature.get_affected_stats(file)
  
  print('=====SCANNED STATS=====')
  print(pokemon)
  print(f'Stat boosted by nature: {nature_modified_stats[0].upper()}')
  print(f'Stat nerfed by nature: {nature_modified_stats[1].upper()}')
  print('=====CALCULATED STATS=====')
  
  pkdata = pb.APIResource('pokemon', args.pokemon.lower())
  stats = pkdata.stats
  
  print('HP EVs is ' + str(calculate_hp_evs(pokemon, stats)))
  for stat in ['atk', 'defense', 'spatk', 'spdef', 'speed']:
     print(f'{stat.upper()} EVs is {str(calculate_non_hp_evs(pokemon, stats, nature_modified_stats, stat))}')

def get_base_stat(stats, stat_name):
  # Convert stats into naming scheme used by API
  if (stat_name == 'atk'):
    stat_name = 'attack'
  if (stat_name == 'spatk'):
    stat_name = 'special-attack'
  if (stat_name == 'spdef'):
    stat_name = 'special-defense'
  return list(filter(lambda x : x.stat.name == stat_name, stats))[0].base_stat


def get_nature_modifier(nature_modified_stats, stat_name):
  if(nature_modified_stats[0] == stat_name):
    return 1.1
  if(nature_modified_stats[1] == stat_name):
    return 0.9
  return 1
  
def get_closest_multiple_of_4_not_higher(val):
  # The stat calculation formula uses some math.floor operations when calculating the resulting stat
  # Since this is a destructive operation, our resulting EV value may be slightly off. We get the closest multiple of 4
  # evs at or below our guess, and then backtest incrementing by multiples of 4 from there to confirm
  val = int(val)
  for i in range(4):
    if ((val - i) % 4 == 0):
      return val - i
 
  
def calculate_hp_evs(pokemon, stats):
  # assume hypertrained/max ivs
  hp_base = get_base_stat(stats, 'hp')
  x = (int(pokemon.hp) - int(pokemon.lvl) - 10)
  y = x * 100
  z = y / int(pokemon.lvl)
  evs_guess = (z - 31 - (2 * hp_base)) * 4
  
  # Might appear negative due to the destructive math.floor usages. Set guess to zero and then backtest to confirm.
  if (evs_guess < 0):
    evs_guess = 0
  evs_guess = get_closest_multiple_of_4_not_higher(evs_guess)    
  
  return backtest_hp_evs(pokemon.lvl, int(pokemon.hp), hp_base, evs_guess)  
  
# stat calcs
# https://bulbapedia.bulbagarden.net/wiki/Stat#Example_2  

def backtest_hp_evs(lvl, real_stat, base_stat, evs_guess):
  # The stat calculation formula has a couple of math.floor calls, which cause us to lose precision when reversing the formula
  # to determine EVs.
  # So once we have a guess that's close, run through the nearby values until we find the correct one.
  backtest_value = determine_hp_stat_value_from_evs(lvl, base_stat, evs_guess)
  
  while(backtest_value != real_stat and evs_guess <= 252):
    print(f'Guessed HP EVs were {str(evs_guess)} ({backtest_value}), but was wrong. Trying {str(evs_guess + 4)}')
    evs_guess += 4
    backtest_value = determine_hp_stat_value_from_evs(lvl, base_stat, evs_guess)
  return evs_guess  
  
def determine_hp_stat_value_from_evs(lvl, base_stat, evs_guess):
  a = 2 * base_stat
  b = a + 31
  c = b + math.floor(evs_guess / 4)
  d = c * int(lvl)
  e = math.floor(d / 100)
  f = e + 10
  g = f + int(lvl)
  return math.floor(g)

def backtest_non_hp_evs(lvl, real_stat, base_stat, nature_factor, stat, evs_guess):
  # The stat calculation formula has a couple of math.floor calls, which cause us to lose precision when reversing the formula
  # to determine EVs.
  # So once we have a guess that's close, run through the nearby values until we find the correct one.
  backtest_value = determine_non_hp_stat_value_from_evs(lvl, base_stat, nature_factor, stat, evs_guess)
  while(backtest_value != real_stat and evs_guess <= 252):
    print(f'Guessed {stat.upper()} EVs were {str(evs_guess)} ({backtest_value}), but was wrong. Trying {str(evs_guess + 4)}')
    evs_guess += 4
    backtest_value = determine_non_hp_stat_value_from_evs(lvl, base_stat, nature_factor, stat, evs_guess)
  return evs_guess  
  
def determine_non_hp_stat_value_from_evs(lvl, base_stat, nature_factor, stat, evs_guess):
  a = 2 * base_stat
  b = a + 31
  c = b + math.floor(evs_guess / 4)
  d = c * int(lvl)
  e = math.floor(d / 100)
  f = e + 5
  g = f * nature_factor
  return math.floor(g)
  
def calculate_non_hp_evs(pokemon, stats, nature_modified_stats, stat):
  # assume hypertrained/max ivs
  nature_factor = get_nature_modifier(nature_modified_stats, stat)
  
  base_stat = get_base_stat(stats, stat)
  iv = 31
  real_stat = int(getattr(pokemon, stat))
  a = real_stat / nature_factor
  b = a - 5
  c = b * 100
  d = c / int(pokemon.lvl)
  e = d - 2 * base_stat
  f = e - iv
  evs_guess = math.floor(4 * f)
  
  # Might appear negative due to the destructive math.floor usages. Set guess to zero and then backtest to confirm.
  if (evs_guess < 0):
    evs_guess = 0
  evs_guess = get_closest_multiple_of_4_not_higher(evs_guess)    
  
  return backtest_non_hp_evs(pokemon.lvl, real_stat, base_stat, nature_factor, stat, evs_guess)  

def parse_ocr_output(output):
  chunks = output.split('\n')
  lvl = 0
  hp = 0
  atk = 0
  spdef = 0
  speed = 0
  spdef = 0
  defense = 0
  
  expecting_hp_chunk = False
  expecting_atk_chunk = False
  expecting_def_chunk = False
  expecting_speed_chunk = False
  
  for chunk in chunks:
    #print(f'CHUNK{chunk}')
    lvl_match = re.search('Lv.* (\d+)', chunk, re.IGNORECASE)
    if(lvl_match):
      lvl = lvl_match.group(1)
      continue
    
    hp_match = re.search('HP.*', chunk)
    if(hp_match):
      expecting_hp_chunk = True
      continue
    if(expecting_hp_chunk):
      hp_value_match = re.search('\d+\/(\d+)', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (hp_value_match):
        hp = hp_value_match.group(1)
        expecting_hp_chunk = False
      continue
    
    atk_match = re.search('Sp. Atk.*Attack', chunk)
    if(atk_match):
       expecting_atk_chunk = True
       continue
    if(expecting_atk_chunk):
      atk_value_match = re.search('.*?(\d+)\D*(\d+)$', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (atk_value_match):
        spatk = atk_value_match.group(1)
        atk = atk_value_match.group(2)
        expecting_atk_chunk = False
      continue
      
    def_match = re.search('Sp. Def.*Defense', chunk)
    if(def_match):
       expecting_def_chunk = True
       continue
    if(expecting_def_chunk):
      def_value_match = re.search('.*?(\d+)\D*(\d+)$', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (def_value_match):
        spdef = def_value_match.group(1)
        defense = def_value_match.group(2)
        expecting_def_chunk = False
      continue
      
    speed_match = re.search('Speed.*', chunk)
    if(speed_match):
      expecting_speed_chunk = True
      continue
    if(expecting_speed_chunk):
      speed_value_match = re.search('(\d+)', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (speed_value_match):
        speed = speed_value_match.group(1)
        expecting_speed_chunk = False
      continue  
    
  return Pokemon(lvl, hp, atk, defense, spatk, spdef, speed)
  
class Pokemon:
  def __init__(self, lvl, hp, atk, defense, spatk, spdef, speed):
    self.lvl = lvl
    self.hp = hp
    self.atk = atk
    self.defense = defense
    self.spatk = spatk
    self.spdef = spdef
    self.speed = speed
    
  def __str__(self):
    
    return '\n'.join(
    [f'Lvl: {self.lvl}',
     f'HP: {self.hp}',
     f'Atk: {self.atk}',
     f'Def: {self.defense}',
     f'Sp Atk: {self.spatk}',
     f'Sp Def: {self.spdef}',
     f'Speed: {self.speed}'])
    
if __name__ == '__main__':
  sys.exit(main())