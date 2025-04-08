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
    self.evs_total = 0
    self.nature = nature
    self.ok = False
    self.msg = ''
  
  def append_msg(self, msg):
    self.msg += msg + '\r\n'

  def evs_valid(self):
    valid = (self.evs_hp is not None and self.evs_hp > 0 and self.evs_hp<= 252 and
                self.evs_atk is not None and self.evs_atk > 0 and self.evs_atk<= 252 and
                self.evs_defense is not None and self.evs_defense > 0 and self.evs_defense<= 252 and
                self.evs_spatk is not None and self.evs_spatk > 0 and self.evs_spatk<= 252 and
                self.evs_spdef is not None and self.evs_spdef > 0 and self.evs_spdef<= 252 and
                self.evs_speed is not None and self.evs_speed > 0 and self.evs_speed<= 252
                )
    
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