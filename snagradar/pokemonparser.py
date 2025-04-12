import evs_calculator
import pokebase as pb
import nature
import process
import copy
from pokemon import Pokemon
from processocrspace import run_ocr
from ocr_parser import parse_ocr_output
from snagexception import SnagException, SkipNatureException

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
  print("Pokemon based on user input, pre-OCR:")
  print(pokemon)
  if (pokemon.nature_valid() and pokemon.base_stats_valid()):
     # Don't bother trying to do any OCR if the user has already told us everything we would get
     # from an image
     print("User-supplied stats mean we don't need an image. Returning early...")
     return parse_pokemon(pokemon)
  print("User-supplied stats were insufficient, trying initial scan.")
  try:
    pokemon = parse(img, pokemon)
    print("Initial scan complete and successful, no need to crop.")
    if (not pokemon.base_stats_valid()):
      raise SnagException('Base stats are not valid. Trying again with cropped version.')
  except: 
    print("After failed initial scan, Pokemon is:")
    print(pokemon)
    print("Secondary scan starting, cropping and scanning again.")
    cropped_pokemon = parse_cropped(img, pokemon)
    if(cropped_pokemon is not None and cropped_pokemon.evs_valid()):
       # Only use the results of the crop if it's actually valid, otherwise go with what we've got.
       pokemon = cropped_pokemon
  print('=====FINAL SCANNED STATS=====')
  print(pokemon)
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
       try:
          varieties = pb.APIResource('pokemon-species', name_guess).varieties
       except AttributeError:
          # It's not a species and not a forme, it's PROBABLY a nickname or foreign name.
          raise SnagException("Could not detect Pokemon Name. Name is either in a non-English language OR has a nickname. Select the pokemon's name from the dropdown and re-scan.")
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
   return pkmn
   
def iterate_through_varieties(pokemon, possible_pokemon):
   exception = None
   possible_varieties = []
   for possible_pkmn in possible_pokemon:
      try:
        pokemon_variety = iterate_through_natures(pokemon, possible_pkmn.stats)
        if (pokemon_variety is not None):
          pokemon_variety.name = possible_pkmn.name
          return pokemon_variety
      except SnagException as e:
         exception = e
   if (possible_varieties.length == 0):
     raise exception
   pokemon_with_lowest_ev_range = min(possible_pkmn, key=lambda x: x.evs_total_range())
   if (possible_varieties.length > 1):
      pokemon_with_lowest_ev_range.append_msg("Multiple possible formes found. This one is our best guess. If it's incorrect, please specify the correct forme from the dropdown.")
   return pokemon_with_lowest_ev_range

def iterate_through_natures(pokemon, stats):
    # I tried writing an OCR script to try and isolate the hex arrows to determine a nature.
    # However, it was too tricky to work as soon as you had lower image quality, so instead we just brute force it - try every nature until we find those where the EV math actually works.
    
    # Nature cannot affect HP stat, this value should be correct    
    hp_evs = evs_calculator.calculate_hp_evs(pokemon, stats)
    
    pokemon.evs_hp = hp_evs
    pokemon.evs_total = pokemon.evs_hp
    
    acceptable_natures = [] # Contains a separate pokemon object for each possible valid nature
    
    nature_affected_stats = ['atk', 'defense', 'spatk', 'spdef', 'speed']

    if pokemon.nature != 'null':
      (nature_up_stat, nature_down_stat) = nature.nature_lookup_reverse(pokemon.nature)
      try:
        for stat in nature_affected_stats:
          evs_calculator.calculate_non_hp_evs(pokemon, stats, [nature_up_stat, nature_down_stat], stat)
      except SkipNatureException:
        return None #The user fed us a nature that results in an impossible pokemon.
      if(not pokemon.evs_valid()):
          return None # Probably a different form
      pokemon.cap_ev_ranges()
      acceptable_natures.append(pokemon)
    else: 
      for nature_up_stat in nature_affected_stats:
          for nature_down_stat in nature_affected_stats:
              if(nature_down_stat == nature_up_stat and nature_up_stat != 'atk'):
                  # only need to check the neutral nature once, not 5 times
                  continue
              candidate_nature = nature.NATURES_LOOKUP[nature_up_stat, nature_down_stat]
              pokemon_copy_for_nature = copy.deepcopy(pokemon)
              pokemon_copy_for_nature.nature = candidate_nature
              try:
                for stat in nature_affected_stats:
                  evs_calculator.calculate_non_hp_evs(pokemon_copy_for_nature, stats, [nature_up_stat, nature_down_stat], stat)
              except SkipNatureException:
                 # one of the stats exceeded 252, so this entire nature should be thrown out
                 continue                    
              if(not pokemon_copy_for_nature.evs_valid()):
                  # This nature is invalid, so try the next one.
                  continue
              
              pokemon_copy_for_nature.cap_ev_ranges()
              acceptable_natures.append(pokemon_copy_for_nature)
    
    if(len(acceptable_natures) == 1):
        return acceptable_natures[0]
    if(len(acceptable_natures) > 1):
       best_guess_pokemon =  min(acceptable_natures, key=lambda x: x.evs_total_range())
       best_guess_pokemon.msg = 'Multiple Natures possible: Please specify one of: ' + ', '.join(p.nature for p in acceptable_natures) + "."
       return best_guess_pokemon
    return None