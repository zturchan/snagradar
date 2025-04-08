#!/var/www/snagradar/venv/python3.13
import sys
sys.path.insert(0, '/var/www/snagradar/snagradar')
sys.path.insert(0, '/var/www/snagradar')
#sys.path.insert(0,"/var/www/snagradar/venv/lib/python3.13/site-packages")

#activate_this = '/var/www/'
#with open(


from snag_flask import create_app
application = create_app()
#application.run(debug=False)
