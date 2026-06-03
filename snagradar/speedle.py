import random
import aiopoke
import pathlib
import constants
from challenge import Challenge

NUMBER_OF_BATTLES = 10
CHANCE_ONE_PLAYER_IN_TAILWIND = (
    0.3  # chance a particular scenario has a tailwind factor present at all
)
CHANCE_PLAYER_TAILWIND = 0.3  # if tailwind is present, chance it's given to the player
CHANCE_PLUS_SPEED_NATURE = 0.5
CHANCE_MAX_SPEED_STAT_POINTS = 0.5
IMAGES_FILEPATH = "static/img/PokemonImages"
IMAGES_MEGAS_SUBFOLDER = "/Megas"


class SpeedleMon:
    def __init__(self, name, base_speed, *args, **kwargs):
        self.name = name
        self.base_speed = base_speed
        # The space ensures we don't treat Meganium as a mega
        self.is_mega = self.name.startswith("Mega ")
        self.api_name = kwargs.get("api_name", None)
        if (self.api_name == None):
            self.api_name = self.name
        self.speed_stat_points = 0
        self.tailwind = None
        self.beneficial_nature = None

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

    async def load_api_values(self):
        # PokeAPI values
        async with aiopoke.AiopokeClient() as client:
            pokemon = await client.get_pokemon(self.api_name)
            self.species = pokemon.species.name
            self.sprite = get_sprite_path(self)

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


async def read_speed_list_from_file(filename, app):
    # Expects a csv file containing the name of a pokemon and it's speed. One pokemon per row.
    pokemon = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if (len(line) == 0):
                continue
            parts = line.split(",")
            name = parts[0]
            speed = int(parts[1])
            api_name = None
            if (len(parts) > 2):
                api_name = parts[2]
            newMon = SpeedleMon(name, speed, app=app, api_name=api_name)

            pokemon.append(newMon)
    return pokemon

async def get_regulation_roster(app):
    # todo, grab these from a DB or something
    path = r"H:\Projects\snagradar\snagradar\speedle\ma-speed-list"
    return await read_speed_list_from_file(path, app)

def get_player_and_villain_teams(roster):
    # We don't want any overlaps of species so we pull all 20 mons at once.
    pokemon = random.sample(roster, NUMBER_OF_BATTLES * 2)
    return pokemon[:10], pokemon[10:]

async def generate_todays_challenge(flaskapp):
    app = flaskapp
    # Generate 10 pokemon for us, and then 10 for the villain.

    roster = await get_regulation_roster()
    player_pokemon_set, villain_pokemon_set = get_player_and_villain_teams(roster)

    for player_mon in player_pokemon_set:
        await player_mon.load_api_values()
    for villain_mon in villain_pokemon_set:
        await villain_mon.load_api_values()
        # Villain mons could have any speed value
        villain_mon.speed_stat_points = None

    challenges = []
    for i in range(len(player_pokemon_set)):
        player_pokemon = player_pokemon_set[i]
        villain_pokemon = villain_pokemon_set[i]

        # no point in comparing 2 mons both with tailwind, it's the same as both without
        any_tailwind = random.random() <= CHANCE_ONE_PLAYER_IN_TAILWIND

        player_pokemon.tailwind = (
            any_tailwind and random.random() <= CHANCE_PLAYER_TAILWIND
        )
        villain_pokemon.tailwind = any_tailwind and not player_pokemon.tailwind

        player_pokemon.beneficial_nature = random.random() <= CHANCE_PLUS_SPEED_NATURE

        # TODO: Allow for other sensible values besides 0 and max, probably species-specific
        player_pokemon.speed_stat_points = (
            constants.MAX_SPEED_STAT_POINTS
            if random.random() <= CHANCE_MAX_SPEED_STAT_POINTS
            else 0
        )

        challenge.append([player_pokemon, villain_pokemon])

    return challenge
