# Silph Scope (nee SnagRadar)
A tool for scanning Pokemon Scarlet &amp; Violet stat pages to display their EVs and other hidden stats. Currently branded as Silph Scope, snagradar was the development name.

## Getting started
1. Install Python 3.12
2. Inside a virtualenv, `pip install requirements.txt`
3. Take a screenshot of the pokemon you want to analyze from Pokemon Scarlet/Violet from the stats page (the one that shows the numbers). See examples in the `img` folder.
4. run with `python main.py -p pikachu /path/to/your/picture.jpg` where pikachu is any pokemon.

# FAQ
1. What about forms?
Specify forms according to the variants names used by https://pokeapi.co/. e.g. If you want info on Landorus Therian, you would run `python main.py -p landorus-therian /path/to/your/picture.jpg`
   
