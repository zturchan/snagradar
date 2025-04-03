import os

from flask import Flask, render_template, request, jsonify
from pokemon import Pokemon
from snagexception import SnagException
import pokemonparser
from werkzeug.utils import secure_filename
from werkzeug.exceptions import InternalServerError
import os

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOAD_FOLDER="upload"
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def snagradar():
        pkmn = Pokemon('', 0,0,0,0,0,0,0) 

        return render_template('snagradar.html', pokemon=pkmn, pokemon_identifier='abomasnow')
    
    @app.errorhandler(SnagException)
    def handle_exception(e):
        print("HANLDING EXCEPTION")
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        # replace the body with JSON
        response = jsonify({
            "code" : e.code,
            "description": e.description
        })
        response.content_type = "application/json"
        return response, e.code
        

    @app.route('/scan_ajax', methods=['POST'])
    def scan_ajax():
        print(request)
        pokemon_name = request.form["pokemon-select"] if "pokemon-select" in request.form else None
        img = request.files["image"]

        path = None
        if img.filename is not '':
            print(img.filename)
            filename = secure_filename(img.filename)
            path = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'], filename)
            print('saving to ' + str(path))

            img.save(path)
        pkmn = pokemonparser.scan(path, pokemon_name, request.form['lvl'],request.form['hp'],request.form['atk'],request.form['defense'],request.form['spatk'],request.form['spdef'],request.form['speed'],request.form['nature'],)
        if (not pkmn.evs_valid):
            raise SnagException('Stats read correctly, but could not determine EVs.')
        print(pkmn)
        response = pkmn.__dict__
        
        os.rm(path)
        return response

    return app