import evs_calculator
import pokebase as pb
import nature
import process
from pokemon import Pokemon
from processocrspace import run_ocr
from ocr_parser import parse_ocr_output
from snagexception import SnagException

def scan(img,
         pokemon_name,
         lvl,
         hp,
         atk,
         defense,
         spatk,
         spdef,
         speed,
         nature):
  # Make a pokemon object with any of the data supplied by user already before looking at the picture 
  pokemon = Pokemon(pokemon_name, lvl, hp, atk, defense, spatk, spdef, speed, nature)
  if (pokemon.nature_valid and pokemon.base_stats_valid()):
     # Don't bother trying to do any OCR if the user has already told us everything we would get
     # from an image
     return parse_pokemon(pokemon)
  try:
    pokemon = parse(img, pokemon)
  except: 
    pokemon = parse_cropped(img, pokemon)
  print('=====SCANNED STATS=====')
  print(pokemon)
  print('=====CALCULATED STATS=====')
  return parse_pokemon(pokemon)

def determine_identifier_from_in_game_name(name):
    # The name we've scanned comes from the in game stats screen.
    # Assuming this name is in English and not a nickname, we need to convert it to the form
    # used by the pokemon API. Most of the time, this will just be a simple lowercase conversion.
    # however, in cases such as pokemon with formes we might need to do more work. 
    # Returns a list of all possibilities
    name_guess = name.lower()
    # Used for pokemon like the paradox mons which have spaces in their names but not their API identifiers
    name_guess = name_guess.replace(" ", "-")

    try:
       pokemon = pb.APIResource('pokemon', name_guess)
       _ = pokemon.stats
       return [pokemon]
    except AttributeError:
       # The pokemon doesn't exist, so maybe it's a forme
       varieties = pb.APIResource('pokemon-species', name_guess).varieties
       possible_pokemon = []
       for variety in varieties:
          pkmn = pb.APIResource('pokemon', variety.pokemon.name)
          try:
              _ = pkmn.stats
              possible_pokemon.append(pkmn)
          except:
             pass
       return possible_pokemon

def parse_pokemon(pokemon):  
  possible_pokemon = determine_identifier_from_in_game_name(pokemon.name)
  if (len(possible_pokemon) == 1):   
    pkdata = possible_pokemon[0]
    stats = pkdata.stats

    pokemon = iterate_through_natures(pokemon, stats)
    return pokemon
  if (len(possible_pokemon) > 1):
     return iterate_through_varieties(pokemon, possible_pokemon)

def parse_cropped(file, pokemon):
    cropped = process.write_cropped(file)
    return parse(cropped, pokemon)
    
def parse(file, pokemon):     
   text = run_ocr(file)
   pkmn = parse_ocr_output(text, pokemon)
   if (not pkmn.base_stats_valid()):
      raise SnagException('Base stats are not valid')
   return pkmn
   
def iterate_through_varieties(pokemon, possible_pokemon):
   exception = None
   for possible_pkmn in possible_pokemon:
      try:
        pokemon_variety = iterate_through_natures(pokemon, possible_pkmn.stats)
        if (pokemon_variety is not None):
          pokemon_variety.name = possible_pkmn.name
          return pokemon_variety
      except SnagException as e:
         exception = e      
   raise exception

def iterate_through_natures(pokemon, stats):
    # I tried writing an OCR script to try and isolate the hex arrows to determine a nature.
    # However, it was too tricky to work as soon as you had lower image quality, so instead we just brute force it - try every nature until we find those where the EV math actually works.
    
    # Nature cannot affect HP stat, this value should be correct    
    hp_evs = evs_calculator.calculate_hp_evs(pokemon, stats)
    
    pokemon.evs_hp = hp_evs
    pokemon.evs_total = pokemon.evs_hp
    other_stat_evs = {}
    
    acceptable_natures = []
    
    nature_affected_stats = ['atk', 'defense', 'spatk', 'spdef', 'speed']

    if pokemon.nature != 'null':
      other_stat_evs = {}
      (nature_up_stat, nature_down_stat) = nature.nature_lookup_reverse(pokemon.nature)
      for stat in nature_affected_stats:
        other_stat_evs[stat] = evs_calculator.calculate_non_hp_evs(pokemon, stats, [nature_up_stat, nature_down_stat], stat)
      evs_total = hp_evs + sum(other_stat_evs.values())
      if(evs_total > 508):
          return None # Probably a different form
      acceptable_natures.append([evs_total, nature_up_stat, nature_down_stat, hp_evs, other_stat_evs])  
    else: 
      for nature_up_stat in nature_affected_stats:
          for nature_down_stat in nature_affected_stats:
              if(nature_down_stat == nature_up_stat):
                  continue
              other_stat_evs = {}
              for stat in nature_affected_stats:
                  other_stat_evs[stat] = evs_calculator.calculate_non_hp_evs(pokemon, stats, [nature_up_stat, nature_down_stat], stat)
              evs_total = hp_evs + sum(other_stat_evs.values())
              if(evs_total > 508):
                  print('total evs=' + str(evs_total))
                  continue;
              acceptable_natures.append([evs_total, nature_up_stat, nature_down_stat, hp_evs, other_stat_evs])
              
    for acceptable_nature in acceptable_natures:
        for stat in ['atk', 'defense', 'spatk', 'spdef', 'speed']:
            evs = acceptable_nature[4][stat]
    if(len(acceptable_natures) == 1):
        mynature = acceptable_natures[0]
        pokemon.nature = nature.NATURES_LOOKUP[(mynature[1], mynature[2])]
        for stat in ['atk', 'defense', 'spatk', 'spdef', 'speed']:
            evs = acceptable_natures[0][4][stat]
            pokemon.evs_total += evs
            setattr(pokemon, 'evs_' + stat, evs)
        return pokemon
    raise SnagException('Multiple Natures possible: Please specify one of: ' + ','.join([nature.NATURES_LOOKUP[(n[1], n[2])] for n in acceptable_natures]))