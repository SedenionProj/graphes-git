import getReposInfo
import getGraphs
import ast
import sys

OUTPUT_DIR = "dossiers_git" # répertoire de sortie
getGraphs.OUTPUT_DIR = OUTPUT_DIR
getReposInfo.OUTPUT_DIR = OUTPUT_DIR

if __name__ == "__main__":
    try:
        lst = ast.literal_eval(sys.argv[2]) # liste des étoiles
        nb = int(sys.argv[1]) # nombre de repos par étoiles
        getReposInfo.get_github_repos_by_stars(nb, lst) # récupère les repos par étoiles dans le fichier $OUTPUT_DIR/info
        getGraphs.get_graphs() # récuper les graphes dans le fichier $OUTPUT_DIR/graphs
    except Exception as e:
        print("ERROR: "+str(e))
        print("utilisation : <nb_repos_per_stars> <stars_List>")
        print('exemple : 8 "[0, 10, 50, 100, 500, 1000]"')