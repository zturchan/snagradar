#!/var/www/snagradar/venv/python3.13
import sys
sys.path.insert(0, '/var/www/snagradar/snagradar')
sys.path.insert(0, '/var/www/snagradar')

from snag_flask import create_app
application = create_app()
