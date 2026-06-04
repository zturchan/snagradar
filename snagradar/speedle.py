import random
import aiopoke
import constants
import speedle_db
from speedlemon import SpeedleMon
from challenge import Challenge

NUMBER_OF_BATTLES = 10
CHANCE_ONE_PLAYER_IN_TAILWIND = (
    0.3  # chance a particular scenario has a tailwind factor present at all
)
CHANCE_PLAYER_TAILWIND = 0.3  # if tailwind is present, chance it's given to the player
CHANCE_PLUS_SPEED_NATURE = 0.5
CHANCE_MAX_SPEED_STAT_POINTS = 0.5

def get_player_and_villain_teams(roster):
    # We don't want any overlaps of species so we pull all 20 mons at once.
    pokemon = random.sample(roster, NUMBER_OF_BATTLES * 2)
    return pokemon[:10], pokemon[10:]

async def generate_todays_challenge():
    challenges_from_db = speedle_db.todays_challenges()
    if (len(challenges_from_db)):
        return challenges_from_db

    # Generate 10 pokemon for us, and then 10 for the villain.

    roster = await speedle_db.read_speed_list_from_db()
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
        villain_pokemon.beneficial_nature = random.random() <= CHANCE_PLUS_SPEED_NATURE

        # TODO: Allow for other sensible values besides 0 and max, probably species-specific
        player_pokemon.speed_stat_points = (
            constants.MAX_SPEED_STAT_POINTS
            if random.random() <= CHANCE_MAX_SPEED_STAT_POINTS
            else 0
        )

        challenges.append(Challenge(player_pokemon, villain_pokemon))

    speedle_db.write_challenges_to_sqlite(challenges)
    return challenges