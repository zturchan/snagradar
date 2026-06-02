import pokebase as pb
import os
import random

NUMBER_OF_BATTLES = 10
CHANCE_ONE_PLAYER_IN_TAILWIND = (
    0.3  # chance a particular scenario has a tailwind factor present at all
)
CHANCE_PLAYER_TAILWIND = 0.3  # if tailwind is present, chance it's given to the player
CHANCE_PLUS_SPEED_NATURE = 0.5
CHANCE_MAX_SPEED_STAT_POINTS = 0.5
MAX_SPEED_STAT_POINTS = 32


class SpeedleMon:
    def __init__(self, name, base_speed, *args, **kwargs):
        # the name used by the api
        self.name = name
        self.base_speed = base_speed
        # User for megas, formes, etc
        self.display_name = kwargs.get("display_name", name)
        self.speed_stat_points = 0
        self.tailwind = None
        self.beneficial_nature = None

    def __str__(self):

        summary = self.display_name + "<br/>"
        if self.speed_stat_points is not None:
            match self.speed_stat_points:
                case 0:
                    summary += "No speed investment"
                case 32:
                    summary += str(MAX_SPEED_STAT_POINTS) + " (Max) speed investment"
                case _:
                    summary += self.speed_stat_points + " speed investment"
            summary += "<br/>"
        if self.beneficial_nature:
            summary += "With a +speed nature (Hasty, Jolly, Naive, and Timid grant +10% speed)<br/>"
        elif self.beneficial_nature is not None:
            summary += "With a neutral speed nature<br/>"

        if self.tailwind:
            summary += "In Tailwind (2x speed)"
        return summary


def read_speed_list_from_file(filename):
    # Expects a csv file containing the name of a pokemon and it's speed. One pokemon per row.
    pokemon = []

    with open(filename) as f:
        for line in f:
            name, speed = line.split(",")
            pokemon.append(SpeedleMon(name, speed))
    return pokemon


def get_regulation_roster():
    # todo, grab these from a DB or something
    path = r"H:\Projects\snagradar\snagradar\speedle\ma-speed-list"
    return read_speed_list_from_file(path)


def get_random_mons(roster, x):
    return random.sample(roster, x)


def generate_todays_challenge():
    # Generate 10 pokemon for us, and then 10 for the villain.

    roster = get_regulation_roster()
    player_pokemon_set = get_random_mons(roster, NUMBER_OF_BATTLES)
    villain_pokemon_set = get_random_mons(roster, NUMBER_OF_BATTLES)

    challenge = []
    for i in range(10):
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
            MAX_SPEED_STAT_POINTS
            if random.random() <= CHANCE_MAX_SPEED_STAT_POINTS
            else 0
        )

        challenge.append([player_pokemon, villain_pokemon])

    return challenge
