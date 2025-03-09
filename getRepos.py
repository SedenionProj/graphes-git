import requests
import ast
import sys

# Remplacer par son token personnel
TOKEN = ""

def getReposInfoByStarsPage(stars:int|tuple, page:int)->dict:
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

def cloneGithubRepos(repos, nbRepos:int=100):
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


        if i==nbRepos-1:
            break


def cloneGithubReposByStars(nbReposPerStars:int, clone:bool, starsList:list[tuple|int]):
    assert nbReposPerStars <=1000, "Impossible de récupérer plus de 1000 repos par fourchette d'étoiles"
    for stars in starsList:
        for page in range(nbReposPerStars//100):
            repos = getReposInfoByStarsPage(stars, page)
            cloneGithubRepos(repos)
        repos = getReposInfoByStarsPage(stars, nbReposPerStars//100)
        cloneGithubRepos(repos, nbReposPerStars%100)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        print("Arguments:", sys.argv[1:])
        lst = ast.literal_eval(sys.argv[3])
        nb = int(sys.argv[1])
        clone = sys.argv[2].lower() == "true"
        print(lst, nb, clone)
        cloneGithubReposByStars(nb, clone, lst)
    else:
        print("utilisation : <nbReposPerStars> <clone> <Stars List>")
        print('exemple : 8 True "[(12,156), (1,2), 5]"')