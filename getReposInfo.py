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

    stars_query = f"{stars[0]}..{stars[1]}" # récupération de la fourchette d'étoiles en format "0..10"

    url = f"https://api.github.com/search/repositories?q=stars:{stars_query}&per_page=100&page={page+1}"

    headers = {
        "Authorization": f"token {TOKEN}", # ajout du token d'authentification dans les headers de la requête
    }

    response = requests.get(url, headers=headers) # envoi de la requête GET à l'API GitHub

    if response.status_code == 200: # si la requête a réussi
        return response.json()
    else:
        print(f"ERROR: {response.status_code}: {response.text}")
        return {}


def write_github_repos(repos, stars_folder, nb_repos:int=100):
    for i, repo in enumerate(repos["items"]): # itération sur les repos de la page courante

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
        rep_info_path = os.path.join(stars_folder, str(repo['id'])+".json") # répertoire $OUTPUT_DIR/info/<stars>/<repo_hash>.json
        
        with open(rep_info_path, "w") as f: # ouverture du fichier $OUTPUT_DIR/info/<stars>/<repo_hash>.json en écriture
            json.dump(d, f) # écriture des infos du repo dans le fichier $OUTPUT_DIR/info/<stars>/<repo_hash>.json

        if i==nb_repos-1: # si on a atteint le nombre de repos à récupérer
            break


def get_github_repos_by_stars(nbReposPerStars:int, stars_list:list[int]):
    print("Récupération des infos...")
    assert nbReposPerStars <= 1000, "Impossible de récupérer plus de 1000 repos par fourchette d'étoiles"

    for i in range(len(stars_list)-1):
        stars = (stars_list[i], stars_list[i+1]) # récupération de la fourchette d'étoiles

        stars_folder = os.path.join(OUTPUT_DIR, "info", f"{stars[0]}-{stars[1]}") # répertoire $OUTPUT_DIR/info/<stars>
        os.makedirs(stars_folder, exist_ok=True) # création du répertoire $OUTPUT_DIR/info/<stars> s'il n'existe pas
        
        for page in range(nbReposPerStars//100): 
            repos = get_repos_info_by_stars_page(stars, page) # récupération des repos de la page courante
            write_github_repos(repos, stars_folder) # écriture des infos dans le fichier $OUTPUT_DIR/info/<stars>/<repo_hash>.json

        if nbReposPerStars%100 == 0:
            continue

        repos = get_repos_info_by_stars_page(stars, nbReposPerStars//100) # récupération des repos de la dernière page
        write_github_repos(repos, stars_folder, nbReposPerStars%100) # écriture des infos dans le fichier $OUTPUT_DIR/info/<stars>/<repo_hash>.json

if __name__ == "__main__":
    try:
        lst = ast.literal_eval(sys.argv[2]) # liste des étoiles
        nb = int(sys.argv[1]) # nombre de repos par étoiles
        get_github_repos_by_stars(nb, lst) # récupère les repos par étoiles dans le fichier $OUTPUT_DIR/info
    except Exception as e:
        print("ERROR: "+str(e))
        print("utilisation : <nb_repos_per_stars> <stars_List>")
        print('exemple : 8 "[0, 10, 50, 100, 500, 1000]"')