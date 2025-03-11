import requests
import ast
import sys
import json

# Remplacer par son token personnel
TOKEN = ""

def get_repos_info_by_stars_page(stars:int|tuple, page:int)->dict:
    '''
    page: numéro de la page avec 0 <= page <= 10
    stars: nombre d'étoiles
    '''
    assert page <=10, "La page courrante doit être inférieur à 10"

    if isinstance(stars, tuple):
        stars_query = f"{stars[0]}..{stars[1]}"
    else:
        stars_query = str(stars)

    url = f"https://api.github.com/search/repositories?q=stars:{stars_query}&per_page=100&page={page+1}"

    headers = {
        "Authorization": f"token {TOKEN}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return {}

def write_initial_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def append_to_json(new_data, filename):
    with open(filename, 'r+') as f:
        data = json.load(f)
        data.append(new_data)
        f.seek(0)
        json.dump(data, f, indent=4)

def write_github_repos(repos, nbRepos:int=100):
    """
    id : identifient unique
    language : langage de programmation
    full_name : usr/repo
    clone_url

    forks_count
    open_issues_count
    size : taille du répo en ko
    stargazers_count : nombre d'étoiles

    created_at     (format : 2014-12-24T17:49:19Z)
    updated_at
    pushed_at
    """
    for i, repo in enumerate(repos["items"]):

        print(f"{i}: {repo['full_name']} ")
        d = {
            "id" : repo['id'],
            "language" : repo['language'],
            "full_name" : repo['full_name'],
            "clone_url" : repo['clone_url'],

            "forks_count" : repo['forks_count'],
            "open_issues_count" : repo['open_issues_count'],
            "size" : repo['size'],
            "stargazers_count" : repo['stargazers_count'],

            "created_at" : repo['created_at'],
            "updated_at" : repo['full_name'],
            "pushed_at" : repo['pushed_at'],
            }
        append_to_json(d, "C:/Users/Gerome/Desktop/graphes-git/dossiers_git/repos_info.json")

        if i==nbRepos-1:
            break


def get_github_repos_by_stars(nbReposPerStars:int, starsList:list[tuple|int]):
    assert nbReposPerStars <=1000, "Impossible de récupérer plus de 1000 repos par fourchette d'étoiles"        
    for stars in starsList:
        for page in range(nbReposPerStars//100):
            repos = get_repos_info_by_stars_page(stars, page)
            write_github_repos(repos)
        repos = get_repos_info_by_stars_page(stars, nbReposPerStars//100)
        write_github_repos(repos, nbReposPerStars%100)


if __name__ == "__main__":
    write_initial_data([], 'C:/Users/Gerome/Desktop/graphes-git/dossiers_git/repos_info.json')
    try:
        print("Arguments:", sys.argv[1:])
        lst = ast.literal_eval(sys.argv[2])
        nb = int(sys.argv[1])
        get_github_repos_by_stars(nb, lst)
    except Exception as e:
        print(e)
        print("utilisation : <nbReposPerStars> <Stars List>")
        print('exemple : 8 "[(12,156), (1,2), 5]"')