from constants import MAX_SPEED_STAT_POINTS

class Challenge:
    def __init__(self, player_pokemon, villain_pokemon, **kwargs):
        self.player_pokemon = player_pokemon
        self.villain_pokemon = villain_pokemon
        self.result = kwargs.get("result", self.determine_winner())

    def determine_winner(self):
        # Return -1 if player underspeeds, 0 if sometimes, 1 if player always outspeeds
        
        player_speed = self.player_pokemon.base_speed + self.player_pokemon.speed_stat_points
        if (self.player_pokemon.beneficial_nature):
            player_speed *= 1.1
        if (self.player_pokemon.tailwind):
            player_speed *= 2
        
        villain_min_speed = self.villain_pokemon.base_speed
        if (self.villain_pokemon.tailwind):
            villain_min_speed *= 2
        
        if (player_speed < villain_min_speed):
            return -1
        
        # Nature is assumed plus, since not available to player.
        villain_max_speed = 1.1 * (self.villain_pokemon.base_speed + MAX_SPEED_STAT_POINTS)
        
        if (self.villain_pokemon.tailwind):
            villain_max_speed *=2
            
        if (player_speed > villain_max_speed):
            return 1
        
        return 0