import math

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
  if(real_stat < backtest_value):
    print('hp does not have 31 IVs. Assuming EVs = 0.')
    return 0
  while(backtest_value != real_stat and evs_guess <= 252):
    #print(f'Guessed HP EVs were {str(evs_guess)} ({backtest_value}), but was wrong. Trying {str(evs_guess + 4)}')
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
  if(real_stat < backtest_value):
    #print(f'{stat.upper()} does not have 31 IVs. Assuming EVs = 0.')
    return 0
  while(backtest_value != real_stat and evs_guess <= 252):
    #print(f'Guessed {stat.upper()} EVs were {str(evs_guess)} ({backtest_value}), but was wrong. Trying {str(evs_guess + 4)}')
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
  
def get_nature_modifier(nature_modified_stats, stat_name):
  if(nature_modified_stats[0] == stat_name):
    return 1.1
  if(nature_modified_stats[1] == stat_name):
    return 0.9
  return 1
  
def get_base_stat(stats, stat_name):
  # Convert stats into naming scheme used by API
  if (stat_name == 'atk'):
    stat_name = 'attack'
  if (stat_name == 'spatk'):
    stat_name = 'special-attack'
  if (stat_name == 'spdef'):
    stat_name = 'special-defense'
  return list(filter(lambda x : x.stat.name == stat_name, stats))[0].base_stat
  
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
