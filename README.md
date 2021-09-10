
WINDOWS:

Ouvrez le terminal de commande avec WIN+R, tapez 'cmd' et Entrée.

Si vous n'avez pas encore Python, installez le, et tapez 'python' pour vérifier (sortez de python avec 'exit()')

Pour vous rendre dans le fichier du projet, tapez cd puis le chemin d'accès, ou aidez vous de la touche TABULATION
Exemple:
C:\Users\Pierre\> cd Desktop (Vous fera parvenir au bureau)

Une fois dans le fichier du projet que vous avez téléchargé, créez un environnement virtuel avec la commande: python -m venv virtualenv

Activez le ensuite avec la commande : virtualenv\Scripts\activate

Puis récupérez les packages Python de requirements.txt avec la commande suivante : pip install -r requirements.txt

Enfin executez le programme en tapant dans la console : chess.py

Ou effectuez un rapport flake8-html avec la commande : flake8 ./chess.py  --format=html --htmldir=flake-report