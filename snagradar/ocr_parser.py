import re
from pokemon import Pokemon

def parse_ocr_output(output, pokemon):
  if (output is None):
    # Happens if the crop failed and didn't get us a good screengrab
    return pokemon
  chunks = output.split('\n')
  lvl = ''
  hp = ''
  atk = ''
  spatk = ''
  speed = ''
  spdef = ''
  defense = ''
  name = ''
  
  expecting_name_chunk = False
  expecting_hp_chunk = False
  expecting_atk_chunk = False
  expecting_spatk_chunk = False
  expecting_def_chunk = False
  expecting_spdef_chunk = False
  expecting_speed_chunk = False
    
  for chunk in chunks:
    # remove whitespace from OCR output
    chunk = "".join(chunk.split())

    change_moves_match = re.search('.*Change.*Moves.*', chunk, re.IGNORECASE)
    if(change_moves_match):
      # We should start looking for the Pokemon's name
      expecting_name_chunk = True
      continue
    if(expecting_name_chunk):
      name = chunk.strip()
      expecting_name_chunk = False
      continue

    lvl_match = re.search(r'[LI][vxy].*?(\d+)', chunk, re.IGNORECASE)
    if(lvl_match):
      lvl = lvl_match.group(1)
      continue
    
    hp_match = re.search('HP.*', chunk)
    if(hp_match):
      expecting_hp_chunk = True
      continue
    if(expecting_hp_chunk):
      hp_value_match = re.search(r'\d+\/(\d+)', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (hp_value_match):
        hp = hp_value_match.group(1)
        expecting_hp_chunk = False      
      continue
    
    # This is for OCRSpace format
    # sometimes the t in atk is parse as l
    spatk_match = re.search(r'.*Sp.A[tl]k.*', chunk)
    if(spatk_match):
       expecting_spatk_chunk = True
       continue
    if(expecting_spatk_chunk):
      spatk_value_match = re.search(r'.*?(\d+).*?$', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (spatk_value_match):
        spatk = spatk_value_match.group(1)
        expecting_spatk_chunk = False
      continue
      
    atk_match = re.search(r'.*?A[tl][tl]a[ckd].*?$', chunk)
    if(atk_match):
       expecting_atk_chunk = True
       continue
    if(expecting_atk_chunk):
      atk_value_match = re.search(r'.*?(\d+).*?$', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (atk_value_match):
        atk = atk_value_match.group(1)
        expecting_atk_chunk = False
      continue
      
    spdef_match = re.search(r'.*?Sp.De[lf].*?', chunk)
    if(spdef_match):
       expecting_spdef_chunk = True
       continue
    if(expecting_spdef_chunk):
      spdef_value_match = re.search(r'.*?(\d+).*$', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (spdef_value_match):
        spdef = spdef_value_match.group(1)
        expecting_spdef_chunk = False
      continue
      
    def_match = re.search('.*De[lf]ense.*', chunk)
    if(def_match):
       expecting_def_chunk = True
       continue
    if(expecting_def_chunk):
      def_value_match = re.search(r'.*?(\d+).*?$', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (def_value_match):
        defense = def_value_match.group(1)
        expecting_def_chunk = False
      continue
      
    speed_match = re.search('.*Speed.*', chunk)
    if(speed_match):
      expecting_speed_chunk = True
      continue
    if(expecting_speed_chunk):
      speed_value_match = re.search(r'(\d+)', chunk)
      # If we find the value we're looking for, log it. If not, continue as this chunk might be noise
      if (speed_value_match):
        speed = speed_value_match.group(1)
        expecting_speed_chunk = False
      continue  
  print("DEBUG - parsing hp = " + str(pokemon.hp))

  if pokemon.name == 'null':
    pokemon.name = name
  pokemon.set_stat('lvl', lvl)
  pokemon.set_stat('hp', hp)
  pokemon.set_stat('atk', atk)
  pokemon.set_stat('defense', defense)
  pokemon.set_stat('spatk', spatk)
  pokemon.set_stat('spdef', spdef)
  pokemon.set_stat('speed', speed)

  return pokemon