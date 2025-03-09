import requests
from bs4 import BeautifulSoup
import subprocess
import os
import shutil
import sys
import ast

OUTPUT_DIR = "dossiers_git"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def cloneGitRepo(repoPath):
    repoName = os.path.basename(repoPath)   # nom et dossier du repo
    try:
        gitFolder = os.path.join(repoName, ".git")  # dossier .git
        destFolder = os.path.join(OUTPUT_DIR, repoName) # dossier de destination
        os.makedirs(destFolder) # on crée le dossier de destination
        subprocess.run(["git", "clone", "https://github.com"+ repoPath], check=True)    # on fait un clonage du repo
        shutil.move(gitFolder, destFolder)  # on déplace le dossier .git
        shutil.rmtree(repoName) # on supprime le dossier repo
    except Exception as e:
        print(f"Erreur traitement {repoName}: {e}")
        if os.path.exists(repoName):
            shutil.rmtree(repoName)

def getGithubReposPage(page, stars, number = 10) -> list:
    '''
    number: nombre de repos à récupérer avec 0 <= number <= 10
    page: numéro de la page avec 0 <= page <= 100
    stars: nombre d'étoiles
    '''
    assert number <= 10, "Le nombre de repos par page doit être inférieur à 10"


    # url des repos github
    if isinstance(stars, tuple):
        url = f"https://github.com/search?q=stars%3A{str(stars[0])}..{str(stars[1])}&type=Repositories&ref=advsearch&l=&l=&p={str(page+1)}"
    elif isinstance(stars, int):
        url = f"https://github.com/search?q=stars%3A{str(stars)}&type=Repositories&ref=advsearch&l=&l=&p={str(page+1)}"

    # on recupère la page
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erreur de chargement pour la page {page} des {stars} étoiles, code : {response.status_code}")
        return
    soup = BeautifulSoup(response.text, "html.parser")

    # on recupere les liens des repos
    githubRepos = []
    i = 0
    for a in soup.select("a.prc-Link-Link-85e08"):

        if(i//2 >= number): # on s'arrete au nombre de repos demandé
            break

        link = a.get("href")    # on recupere le lien
        if link[:7] in ["/topics", "https:/"]:   # on ignore les liens qui ne sont pas des repos
            continue
        i+=1

        if i%2 == 0:    # on ignore autres liens contenant "/stargazers"
            continue

        githubRepos.append(link)

    return githubRepos

def cloneGithubReposByStars( stars:list[tuple|int], nbReposPerStars:int, clone:bool):
    
    assert nbReposPerStars <= 1000, "Le nombre de repos par étoile doit être inférieur à 1000"
    
    for star in stars:
        L = []
        for page in range(nbReposPerStars//10):
            # on recupere les 10 premiers repos
            listeRep = getGithubReposPage(page, star)   
            if listeRep is not None:
                L += listeRep
        # on recupere les repos restants
        listeRep = getGithubReposPage(nbReposPerStars//10, star, nbReposPerStars%10)  
        if listeRep is not None:
            L += listeRep
        
        if clone:
            for rep in L:
                cloneGitRepo(rep)
        else:
            print(L)

'''
todo: nb etoiles, fork, date de création, derniere utilisation, vérifier le graphes généré correspond bien au repo
chercher autre type de graphes, comprendre .git

https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28
100 par page, 10 page max
https://api.github.com/search/repositories?q=stars:>=100&per_page=100&page=1

repoName.json, avec les infos
'''

if __name__ == "__main__":
    if len(sys.argv) == 4:
        print("Arguments:", sys.argv[1:])
        lst = ast.literal_eval(sys.argv[3])
        nb = int(sys.argv[1])
        clone = sys.argv[2].lower() == "true"
        print(lst, nb, clone)
        cloneGithubReposByStars(lst, nb, clone)
    else:
        print("utilisation : <nbReposPerStars> <clone> <nbStars>")
        print('exemple : 8 True "[(12,156), (1,2), 5]"')