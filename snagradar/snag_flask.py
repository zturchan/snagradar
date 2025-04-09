import os
import pokemonparser
from flask import Flask, render_template, request, jsonify
from pokemon import Pokemon
from snagexception import SnagException
from werkzeug.utils import secure_filename

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        UPLOAD_FOLDER="upload"
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    try:
        os.makedirs(os.path.join(app.instance_path, app.config['UPLOAD_FOLDER']))
    except OSError:
        pass

    @app.route('/')
    def snagradar():
        pkmn = Pokemon('', 0,0,0,0,0,0,0) 

        return render_template('scan.html', pokemon=pkmn, pokemon_identifier='abomasnow')
    
    @app.errorhandler(SnagException)
    def handle_exception(e):
        print("HANLDING EXCEPTION: " + str(e.description))
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
        if img.filename != '':
            filename = secure_filename(img.filename)
            path = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'], filename)

            img.save(path)
        pkmn = pokemonparser.scan(path, pokemon_name, request.form['lvl'],request.form['hp'],request.form['atk'],request.form['defense'],request.form['spatk'],request.form['spdef'],request.form['speed'],request.form['nature'],)
        if (not pkmn.evs_valid()):
            pkmn.msg = "Some stats could not be scanned - please manually enter the missing values and re-scan."
        response = pkmn.__dict__
        
        os.remove(path)
        return response

    @app.route('/howitworks', methods=['GET'])
    def how_it_works():
        return render_template('howitworks.html')
    return app