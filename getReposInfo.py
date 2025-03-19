import os
import requests
import ast
import sys
import json

# Remplacer par son token personnel
TOKEN = ""
OUTPUT_DIR = "dossiers_git"

def get_repos_info_by_stars_page(stars:tuple, page:int)->dict:
    '''
    page: numéro de la page avec 0 <= page <= 10
    stars: nombre d'étoiles
    '''
    assert page <=10, "La page courrante doit être inférieur à 10"

    stars_query = f"{stars[0]}..{stars[1]}"

    url = f"https://api.github.com/search/repositories?q=stars:{stars_query}&per_page=100&page={page+1}"

    headers = {
        "Authorization": f"token {TOKEN}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"ERROR: {response.status_code}: {response.text}")
        return {}


def write_github_repos(repos, stars_folder, nb_repos:int=100):
    for i, repo in enumerate(repos["items"]):

        d = {
            "id" : repo['id'],
            "language" : repo['language'],
            "name" : repo['name'],
            "clone_url" : repo['clone_url'],

            "forks_count" : repo['forks_count'],
            "open_issues_count" : repo['open_issues_count'],
            "size" : repo['size'],
            "stargazers_count" : repo['stargazers_count'],

            "created_at" : repo['created_at'],
            "pushed_at" : repo['pushed_at'],
            }
        rep_info_path = os.path.join(stars_folder, str(repo['id'])+".json")
        
        with open(rep_info_path, "w") as f:
            json.dump(d, f)

        if i==nb_repos-1:
            break


def get_github_repos_by_stars(nbReposPerStars:int, stars_list:list[int]):
    print("Récupération des infos...")
    assert nbReposPerStars <=1000, "Impossible de récupérer plus de 1000 repos par fourchette d'étoiles"        
    for i in range(len(stars_list)-1):
        stars = (stars_list[i], stars_list[i+1])

        stars_folder = os.path.join(OUTPUT_DIR, "info", f"{stars[0]}-{stars[1]}")
        os.makedirs(stars_folder, exist_ok=True)
        
        for page in range(nbReposPerStars//100):
            repos = get_repos_info_by_stars_page(stars, page)
            write_github_repos(repos, stars_folder)
        repos = get_repos_info_by_stars_page(stars, nbReposPerStars//100)
        write_github_repos(repos, stars_folder, nbReposPerStars%100)

''' todo
library, inverser les arretes, un seul main -> recup graphes, info sur graphes, commentaires
définir les intervalles étoiles intéresent et faire des statistiques,
->  cree un dossier graphe/fourchette_etoile, dossier info/fourchette_etoile

stats: (jupyter)
distribution des degrés entrants et degrés sortants et distribution totale (entrants+sortants+total) (nb entré entrant, nb entré)
[0, 5, 10], 0 degré 1, 5, degré 2, 10, degré 3..., (3 listes), (by networkX, degree_centrality)
les puits : noeuds sortant degré 0,
ratio merge/commit
ratio merge/total_noeuds
ratio commit/total_noeuds
distribution : [0, 5, 10]/3
autres...
'''

if __name__ == "__main__":
    try:
        lst = ast.literal_eval(sys.argv[2])
        nb = int(sys.argv[1])
        get_github_repos_by_stars(nb, lst)
    except Exception as e:
        print("ERROR: "+str(e))
        print("utilisation : <nb_repos_per_stars> <stars_List>")
        print('exemple : 8 "[0, 10, 50, 100, 500, 1000]"')