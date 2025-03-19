import getReposInfo
import getGraphs
import ast
import sys

OUTPUT_DIR = "dossiers_git"
getGraphs.OUTPUT_DIR = OUTPUT_DIR
getReposInfo.OUTPUT_DIR = OUTPUT_DIR

if __name__ == "__main__":
    try:
        lst = ast.literal_eval(sys.argv[2])
        nb = int(sys.argv[1])
        getReposInfo.get_github_repos_by_stars(nb, lst)
        getGraphs.get_graphs()
    except Exception as e:
        print("ERROR: "+str(e))
        print("utilisation : <nb_repos_per_stars> <stars_List>")
        print('exemple : 8 "[0, 10, 50, 100, 500, 1000]"')