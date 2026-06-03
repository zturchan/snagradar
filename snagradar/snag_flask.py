import os
import pokemonparser
from speedle import generate_todays_challenge
from flask import Flask, render_template, request, jsonify
from pokemon import Pokemon
from snagexception import SnagException
from werkzeug.utils import secure_filename
from fileutil import cleanup


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(UPLOAD_FOLDER="upload")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    try:
        os.makedirs(os.path.join(app.instance_path, app.config["UPLOAD_FOLDER"]))
    except OSError:
        pass

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/speedle")
    def speedle():
        return render_template("speedle.html", page="speedle")

    @app.route("/scan")
    def snagradar():
        pkmn = Pokemon("", 0, 0, 0, 0, 0, 0, 0)

        return render_template(
            "scan.html", pokemon=pkmn, pokemon_identifier="abomasnow", page="scan"
        )

    @app.errorhandler(SnagException)
    def handle_exception(e):
        print("HANLDING EXCEPTION: " + str(e.description))
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        # replace the body with JSON
        response = jsonify({"code": e.code, "description": e.description})
        response.content_type = "application/json"
        return response, e.code

    @app.route("/scan_ajax", methods=["POST"])
    def scan_ajax():
        pokemon_name = (
            request.form["pokemon-select"] if "pokemon-select" in request.form else None
        )
        img = request.files["image"]

        path = None
        if img.filename != "":
            filename = secure_filename(img.filename)
            path = os.path.join(
                app.instance_path, app.config["UPLOAD_FOLDER"], filename
            )

            img.save(path)
        else:
            if pokemon_name is None or pokemon_name == "null":
                raise SnagException(
                    "You must supply an image or select a Pokemon name."
                )
        print("About to start scanning:")
        pkmn = pokemonparser.scan(
            path,
            pokemon_name,
            request.form["lvl"],
            request.form["hp"],
            request.form["atk"],
            request.form["defense"],
            request.form["spatk"],
            request.form["spdef"],
            request.form["speed"],
            request.form["nature"],
        )
        if pkmn is None:
            raise SnagException(
                "Could not construct a Pokemon that matches these stats. Double check that you entered any stats/level/nature correctly, or make a github issue if you are sure you've entered valid data."
            )
        if pkmn.evs_valid() == False:
            pkmn.msg = "Some stats could not be scanned - please manually enter the missing values and re-scan."
        response = pkmn.__dict__

        if path is not None:
            cleanup(path)
        return response

    @app.route("/scan_documentation", methods=["GET"])
    def how_it_works():
        return render_template("howitworks.html")

    @app.route("/daily_challenge", methods=["GET"])
    async def daily_challenge():
        challenge_set = await generate_todays_challenge(app)
        return render_template("daily.html", challenge=challenge_set)

    return app
