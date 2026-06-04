import aiopoke
import constants
import pathlib

IMAGES_FILEPATH = "static/img/PokemonImages"
IMAGES_MEGAS_SUBFOLDER = "/Megas"

def get_sprite_path(pokemon):
    folder = IMAGES_FILEPATH if not pokemon.is_mega else IMAGES_FILEPATH + IMAGES_MEGAS_SUBFOLDER
    # Normal sprites have filename "XXXX Name Form.png"
    # - XXXX is the pokemon number and can be ignored - it's just a relic from the download pack I used
    # - Form is optional
    # - Megas are contained in the megas subfolder, and use the same naming scheme except they do not have the number.

    try:
        if (pokemon.is_mega):
            return folder + "/" + pokemon.species.replace("-", " ") + ".png"
        if (pokemon.species.lower() != pokemon.api_name.lower()):
            # This means we're an alternate form, but not a mega
            file_stem = pokemon.api_name.replace("-", " ")
            pattern = f"*{file_stem}.png"
            sprite = sorted(pathlib.Path(folder).glob(pattern, case_sensitive=False))[0]
            return sprite
        pattern = f"*{pokemon.species}.png"
        sprite = sorted(pathlib.Path(folder).glob(pattern, case_sensitive=False))[0]
        return sprite
    except:
        return "notfound.png"



class SpeedleMon:
    def __init__(self, name, base_speed, *args, **kwargs):
        self.name = name
        self.base_speed = base_speed
        # The space ensures we don't treat Meganium as a mega
        self.is_mega = self.name.startswith("Mega ")
        self.api_name = kwargs.get("api_name", None)
        if (self.api_name == None):
            self.api_name = self.name
        self.speed_stat_points = kwargs.get("speed_stat_points", 0)
        self.tailwind = kwargs.get("tailwind", None)
        self.beneficial_nature = kwargs.get("beneficial_nature", None)
        self.species = kwargs.get("species", None)
        self.sprite = kwargs.get("sprite", None)

    def __str__(self):
        summary = ""
        if self.speed_stat_points is not None:
            match self.speed_stat_points:
                case 0:
                    summary += "No speed investment"
                case 32:
                    summary += str(constants.MAX_SPEED_STAT_POINTS) + " (Max) speed investment"
                case _:
                    summary += self.speed_stat_points + " speed investment"
            summary += "<br/>"
        if self.beneficial_nature:
            summary += "<span title='Hasty, Jolly, Naive, and Timid grant +10% speed' class='nature-desc'>With a +speed nature</span><br/>"
        elif self.beneficial_nature is not None:
            summary += "With a neutral speed nature<br/>"

        if self.tailwind:
            summary += "In Tailwind (2x speed)"
        return summary

    def speed_at_lvl_50(self, investment):
        return self.base_speed + constants.CHAMPIONS_DEFAULT_SPEED_MODIFIER + investment

    async def load_api_values(self):
        # PokeAPI values
        async with aiopoke.AiopokeClient() as client:
            pokemon = await client.get_pokemon(self.api_name)
            self.species = pokemon.species.name
            self.sprite = get_sprite_path(self)
