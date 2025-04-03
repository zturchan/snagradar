#Increased stat, decreased stat
NATURES_LOOKUP = {
    ('',''): 'Hardy',
    ('atk','defense'): 'Lonely',
    ('atk','speed'): 'Brave',
    ('atk','spatk'): 'Adamant',
    ('atk','spdef'): 'Naught',
    ('defense','atk'): 'Bold',
    ('defense','speed'): 'Relaxed',
    ('defense','spatk'): 'Impish',
    ('defense','spdef'): 'Lax',
    ('speed','atk'): 'Timid',
    ('speed','defense'): 'Hasty',
    ('speed','spatk'): 'Jolly',
    ('speed','spdef'): 'Naive',
    ('spatk','atk'): 'Modest',
    ('spatk','defense'): 'Calm',
    ('spatk','speed'): 'Quiet',
    ('spatk','spdef'): 'Rash',
    ('spdef','atk'): 'Calm',
    ('spdef','defense'): 'Gentle',
    ('spdef','speed'): 'Sassy',
    ('spdef','spatk'): 'Careful'
}

def nature_lookup_reverse(nature):
    # Given the nature, get the affected stats
    return list(NATURES_LOOKUP.keys())[list(NATURES_LOOKUP.values()).index(nature)]