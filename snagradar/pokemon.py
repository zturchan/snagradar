class Pokemon:
  def __init__(self, name, lvl, hp, atk, defense, spatk, spdef, speed, nature=None):
    self.name = name
    self.lvl = int(lvl) if isinstance(lvl, int) or len(lvl) > 0 else None
    self.hp = int(hp) if isinstance(hp, int) or len(hp) > 0 else None
    self.atk = int(atk) if isinstance(atk, int) or len(atk) > 0 else None
    self.defense = int(defense) if isinstance(defense, int) or len(defense) > 0 else None
    self.spatk = int(spatk) if isinstance(spatk, int) or len(spatk) > 0 else None
    self.spdef = int(spdef) if isinstance(spdef, int) or len(spdef) > 0 else None
    self.speed = int(speed) if isinstance(speed, int) or len(speed) > 0 else None
    self.evs_hp = 0
    self.evs_atk = 0
    self.evs_defense = 0
    self.evs_spatk = 0
    self.evs_spdef = 0
    self.evs_speed = 0
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
    unaccounted_for_evs = 510 - self.evs_hp - self.evs_atk - self.evs_defense - self.evs_spatk - self.evs_spdef - self.evs_speed
    self.evs_range_hp = (self.evs_range_hp[0], min(self.evs_range_hp[1], self.evs_range_hp[0] + unaccounted_for_evs))
    self.evs_range_atk = (self.evs_range_atk[0], min(self.evs_range_atk[1], self.evs_range_atk[0] + unaccounted_for_evs))
    self.evs_range_defense = (self.evs_range_defense[0], min(self.evs_range_defense[1], self.evs_range_defense[0] + unaccounted_for_evs))
    self.evs_range_spatk = (self.evs_range_spatk[0], min(self.evs_range_spatk[1], self.evs_range_spatk[0] + unaccounted_for_evs))
    self.evs_range_spdef = (self.evs_range_spdef[0], min(self.evs_range_spdef[1], self.evs_range_spdef[0] + unaccounted_for_evs))
    self.evs_range_speed = (self.evs_range_speed[0], min(self.evs_range_speed[1], self.evs_range_speed[0] + unaccounted_for_evs))

  def evs_total_range(self):
    # This is mostly just a measure of how confident we are that this pokemon representation is correct.
    # If this = 0, it's absolutely correct. The bigger it is, the less certain we are about the specifics of the pokemon.
    return ((self.evs_range_hp[1] - self.evs_range_hp[0]) +
      (self.evs_range_atk[1] - self.evs_range_atk[0]) +
      (self.evs_range_defense[1] - self.evs_range_defense[0]) +
      (self.evs_range_spatk[1] - self.evs_range_spatk[0]) +
      (self.evs_range_spdef[1] - self.evs_range_spdef[0]) +
      (self.evs_range_speed[1] - self.evs_range_speed[0]))

  def append_msg(self, msg):
    self.msg += msg + '<br/>'

  def evs_valid(self):
    valid = (self.base_stats_valid() == True and
             self.evs_hp is not None and self.evs_hp >= 0 and self.evs_hp<= 252 and
             self.evs_atk is not None and self.evs_atk >= 0 and self.evs_atk<= 252 and
             self.evs_defense is not None and self.evs_defense >= 0 and self.evs_defense<= 252 and
             self.evs_spatk is not None and self.evs_spatk >= 0 and self.evs_spatk<= 252 and
             self.evs_spdef is not None and self.evs_spdef >= 0 and self.evs_spdef<= 252 and
             self.evs_speed is not None and self.evs_speed >= 0 and self.evs_speed<= 252)
    
    if(valid):
      return True
    print("EVS INVALID:")
    print(self)
    return False

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
    valid = self.nature is not None and self.is_valid()
    if (valid):
      return valid
    print("NATURE INVALID")
    return valid
    
  def __str__(self):
    return '\n'.join(
    [f'Lvl: {self.lvl}',
     f'HP: {self.hp}',
     f'Atk: {self.atk}',
     f'Def: {self.defense}',
     f'Sp Atk: {self.spatk}',
     f'Sp Def: {self.spdef}',
     f'Speed: {self.speed}'])
