class SnagException(Exception):
    code = 500
    description = 'An error occurred while parsing your stats'
    def __init__(self, msg):
        self.code = 500
        self.description = msg

class SkipNatureException(Exception):
    def __init__(self, msg):
        self.description = "Skipping Nature: " + msg