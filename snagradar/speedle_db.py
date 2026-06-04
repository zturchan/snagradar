import sqlite3
import datetime
from challenge import Challenge
from speedlemon import SpeedleMon
SQLITE_DB_FILENAME = "speedle.db"

def get_connection():
    con = sqlite3.connect(SQLITE_DB_FILENAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    sqlite3.register_adapter(datetime.date, adapt_date_iso)
    sqlite3.register_converter("date", convert_date)
    sqlite3.register_adapter(SpeedleMon, adapt_speedlemon)
    sqlite3.register_converter("Speedlemon", convert_speedlemon)

    create_initial_db(con)
    return con

def create_initial_db(con):
    cursor = con.cursor()
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_challenge_pokemon(
                    challenge_id INTEGER PRIMARY KEY,
                    Date date,
                    player_pokemon Speedlemon,
                    villain_pokemon Speedlemon,
                    result INTEGER
                    )
                """)

    cursor.execute("""
                CREATE TABLE IF NOT EXISTS base_speeds(
                    pokemon_api_name TEXT PRIMARY KEY,
                    base_speed INTERGER )
                """)
    con.commit()

def adapt_speedlemon(speedlemon):
    return f"""
{speedlemon.name};
{speedlemon.base_speed};
{speedlemon.api_name};
{speedlemon.speed_stat_points};
{speedlemon.tailwind};
{speedlemon.beneficial_nature};
{speedlemon.species};
{speedlemon.sprite};
"""

def decode_boolean(bytes):
    return str(bytes.decode("utf-8").strip()) != str(False)

def convert_speedlemon(s):
    components = s.split(b";")
    try:
        speed_stat_points = int(components[3])
    except:
        speed_stat_points = None

    return SpeedleMon(
        components[0].decode("utf-8"),
        int(components[1]),
        api_name=components[2].decode("utf-8"),
        speed_stat_points = speed_stat_points,
        tailwind=decode_boolean(components[4]),
        beneficial_nature=decode_boolean(components[5]),
        species=components[6].decode("utf-8"),
        sprite=components[7].decode("utf-8")
    )

def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()

def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val.decode())



def write_challenges_to_sqlite(challenges):
    con = get_connection()
    now = datetime.datetime.now().date()
    for challenge in challenges:
        con.executemany("INSERT INTO daily_challenge_pokemon(date, player_pokemon, villain_pokemon, result) VALUES(?,?,?,?)",
                        [(now, challenge.player_pokemon, challenge.villain_pokemon, challenge.result)])
    con.commit()
    con.close()

# todo, the challenge is parsing right, but the pokemon are still in their converted forms.
def parse_challenge(challenge_row):
    return Challenge(challenge_row[1], challenge_row[2], date=challenge_row[0], result=challenge_row[3])

def challenges_for_date(date):
    print(date)
    con = get_connection()
    cur = con.execute(f"SELECT date, player_pokemon, villain_pokemon, result FROM daily_challenge_pokemon WHERE DATE=?", (date,))
    challenges = []
    for c in cur.fetchall():
        challenges.append(parse_challenge(c))
    con.close()
    return challenges

def todays_challenges():
    return challenges_for_date(datetime.datetime.now().date())