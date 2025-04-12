class Pokemon:
  def __init__(self, name, lvl, hp, atk, defense, spatk, spdef, speed, nature=None):
    self.name = name
    self.lvl = int(lvl) if (isinstance(lvl, int) or len(lvl) > 0) and int(lvl) > 0 else None
    self.hp = int(hp) if (isinstance(hp, int) or len(hp) > 0) and int(hp) > 0 else None
    self.atk = int(atk) if (isinstance(atk, int) or len(atk) > 0) and int(atk) > 0 else None
    self.defense = int(defense) if (isinstance(defense, int) or len(defense) > 0) and int(speed) > 0 else None
    self.spatk = int(spatk) if (isinstance(spatk, int) or len(spatk) > 0) and int(spatk) > 0 else None
    self.spdef = int(spdef) if (isinstance(spdef, int) or len(spdef) > 0) and int(spdef) > 0 else None
    self.speed = int(speed) if (isinstance(speed, int) or len(speed) > 0) and int(speed) > 0 else None
    self.evs_range_hp = (0,0)
    self.evs_range_atk = (0,0)
    self.evs_range_defense = (0,0)
    self.evs_range_spatk = (0,0)
    self.evs_range_spdef = (0,0)
    self.evs_range_speed = (0,0)
    self.nature = nature
    self.ok = False
    self.msg = ''

  def set_ev_range(self, stat, min, max):
    match stat:
      case 'hp':
        self.evs_range_hp = (min, max)
      case 'atk':
        self.evs_range_atk = (min, max)
      case 'defense':
        self.evs_range_defense = (min, max)
      case 'spatk':
        self.evs_range_spatk = (min, max)
      case 'spdef':
        self.evs_range_spdef = (min, max)
      case 'speed':
        self.evs_range_speed = (min, max)

  def cap_ev_ranges(self):
    # EV ranges should not imply that EVs could be added that would exceed 510.
    unaccounted_for_evs = (510
                           - self.evs_range_hp[0]
                           - self.evs_range_atk[0]
                           - self.evs_range_defense[0]
                           - self.evs_range_spatk[0]
                           - self.evs_range_spdef[0]
                           - self.evs_range_speed[0])
    self.evs_range_hp = (self.evs_range_hp[0], min(self.evs_range_hp[1], self.evs_range_hp[0] + unaccounted_for_evs))
    self.evs_range_atk = (self.evs_range_atk[0], min(self.evs_range_atk[1], self.evs_range_atk[0] + unaccounted_for_evs))
    self.evs_range_defense = (self.evs_range_defense[0], min(self.evs_range_defense[1], self.evs_range_defense[0] + unaccounted_for_evs))
    self.evs_range_spatk = (self.evs_range_spatk[0], min(self.evs_range_spatk[1], self.evs_range_spatk[0] + unaccounted_for_evs))
    self.evs_range_spdef = (self.evs_range_spdef[0], min(self.evs_range_spdef[1], self.evs_range_spdef[0] + unaccounted_for_evs))
    self.evs_range_speed = (self.evs_range_speed[0], min(self.evs_range_speed[1], self.evs_range_speed[0] + unaccounted_for_evs))

  def evs_total_range(self):
    # This is mostly just a measure of how confident we are that this pokemon representation is correct.
    # If this = 0, it's absolutely correct. The bigger it is, the less certain we are about the specifics of the pokemon.
    delta = 0
    for stat in ['hp', 'atk', 'defense', 'spatk', 'spdef', 'speed']:
      statValue = getattr(self, stat)
      # We do this because if we don't have stat values because e.g. we couldn't parse them, that shouldn't impact the more likely nature
      if (statValue is not None and statValue > 0):
        ev_range = getattr(self, 'evs_range_' + stat)
        delta += ev_range[1] - ev_range[0]

    return ((self.evs_range_hp[1] - self.evs_range_hp[0]) +
      (self.evs_range_atk[1] - self.evs_range_atk[0]) +
      (self.evs_range_defense[1] - self.evs_range_defense[0]) +
      (self.evs_range_spatk[1] - self.evs_range_spatk[0]) +
      (self.evs_range_spdef[1] - self.evs_range_spdef[0]) +
      (self.evs_range_speed[1] - self.evs_range_speed[0]))

  def append_msg(self, msg):
    self.msg += msg + '<br/>'

  def evs_valid(self):
    minimum_evs_totals = (self.evs_range_hp[0]
                          + self.evs_range_atk[0]
                          + self.evs_range_defense[0]
                          + self.evs_range_spatk[0]
                          + self.evs_range_spdef[0]
                          + self.evs_range_speed[0])
    valid = (minimum_evs_totals <= 508 and
             self.evs_range_hp[0] is not None and self.evs_range_hp[0] >= 0 and self.evs_range_hp[0] <= 252 and
             self.evs_range_atk[0] is not None and self.evs_range_atk[0] >= 0 and self.evs_range_atk[0] <= 252 and
             self.evs_range_defense[0] is not None and self.evs_range_defense[0] >= 0 and self.evs_range_defense[0] <= 252 and
             self.evs_range_spatk[0] is not None and self.evs_range_spatk[0] >= 0 and self.evs_range_spatk[0] <= 252 and
             self.evs_range_spdef[0] is not None and self.evs_range_spdef[0] >= 0 and self.evs_range_spdef[0] <= 252 and
             self.evs_range_speed[0] is not None and self.evs_range_speed[0] >= 0 and self.evs_range_speed[0] <= 252)
    
    if(valid):
      return True
    print("EVS INVALID")
    self.print_evs()
    return False
  
  def print_evs(self):
    print('HP: ' + str(self.evs_range_hp))
    print('ATK: ' + str(self.evs_range_atk))
    print('DEF: ' + str(self.evs_range_defense))
    print('SPATK: ' + str(self.evs_range_spatk))
    print('SPDEF: ' + str(self.evs_range_spdef))
    print('SPEED: ' + str(self.evs_range_speed))

  def base_stats_valid(self):
    valid = (self.lvl is not None and self.lvl > 0 and
                self.hp is not None and self.hp > 0 and
                self.atk is not None and self.atk > 0 and
                self.defense is not None and self.defense > 0 and
                self.spatk is not None and self.spatk > 0 and
                self.spdef is not None and self.spdef > 0 and
                self.speed is not None and self.speed > 0)
    
    if(valid):
      return True
    print("BASE STATS INVALID:")
    print(self)
    return False  
  
  def nature_valid(self):
    valid = self.nature is not None
    if (valid):
      return valid
    print("NATURE INVALID:" + self.nature)
    return valid
    
  def set_stat(self, stat, value):
    print("Attempting to Update stat: " + stat + " with new value: " + str(value))
    if(getattr(self, stat) is None and value is not None and len(value) > 0 and int(value) > 0):
      setattr(self, stat, int(value))
    else:
      print("New value was not valid, " + stat + " remains at " + str(getattr(self, stat)))

  def is_valid(self):
    return self.nature_valid() and self.base_stats_valid() and self.evs_valid()

  def __str__(self):
    return '\n'.join(
    [f'Lvl: {self.lvl}',
     f'HP: {self.hp}',
     f'Atk: {self.atk}',
     f'Def: {self.defense}',
     f'Sp Atk: {self.spatk}',
     f'Sp Def: {self.spdef}',
     f'Speed: {self.speed}'])
