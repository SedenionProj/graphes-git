import subprocess
import os
import json
import git
import networkx as nx
from networkx import DiGraph
import pickle

OUTPUT_DIR = "dossiers_git"

def load_json(file_path)->dict:
    with open(file_path) as f:
        return json.load(f) # chargement du fichier json

def save_graph(file_path, graph):
    with open(file_path, 'wb') as f:
        pickle.dump(graph, f, pickle.HIGHEST_PROTOCOL) # sauvegarde du graphe dans le fichier file_path

def process_repository(repo_path, output_file_path):
    repo = git.Repo(repo_path) # ouverture du repo
    g = {}
    node_info = {}
    for commit in repo.iter_commits('--all'): # iteration sur tous les commits du repo
        commit_hash = str(commit)[:7] # hash du commit
        parents = [str(parent)[:7] for parent in commit.parents] # parents du commit
        if commit_hash not in g: # si le commit n'est pas deja dans le graphe
            g[commit_hash] = set() # ajout du commit au graphe
        g[commit_hash].update(parents) # ajout des parents au commit


        color = 'lightblue' # couleur bleu clair par defaut
        if len(parents)>1:
            if(len({str(parent.author) for parent in commit.parents})>1):
                color = 'orange' # couleur orange pour les merges de commits de differents utilisateurs
            else:
                color = 'red' # couleur rouge pour les merges sinon

        node_info[commit_hash] = {
            'color': color  # ajout de la couleur dans les metadonnee
        }
    repo.close()
    graph = nx.DiGraph(g) # creation du graphe oriente a partir du dictionnaire g
    nx.set_node_attributes(graph, node_info) # ajout des matadonnees

    graph = DiGraph.reverse(graph)

    save_graph(output_file_path, graph) # sauvegarde du graphe dans le fichier output_file_path

def load_graph_from_json(file_path, out_dir):
    try:
        file = load_json(file_path) # chargement du fichier json
        subprocess.run(["git", "clone", file["clone_url"]], check=True) # clonage du repo
        process_repository(file["name"], os.path.join(out_dir, str(file["id"]))) # traitement du repo
        os.system('rmdir /S /Q "{}"'.format(file["name"])) # suppression du repo clone
    except Exception as e:
        print(f"Erreur lors du traitement du fichier {file_path} : {e}")

def get_graphs():
    print("Recuperation des graphes...")

    info_path = os.path.join(OUTPUT_DIR, "info") # repertoire $OUTPUT_DIR/info
    graphs_path = os.path.join(OUTPUT_DIR, "graphs") # repertoire $OUTPUT_DIR/graphs
    info_star_folders = [f for f in os.listdir(info_path) if os.path.isdir(os.path.join(info_path, f))] # liste des repertoires dans $OUTPUT_DIR/info

    for folder_name in info_star_folders: # pour chaque repertoire dans $OUTPUT_DIR/info
        graphs_path_stars = os.path.join(graphs_path, folder_name) # repertoire $OUTPUT_DIR/graphs/<stars>
        info_path_stars = os.path.join(info_path, folder_name) # repertoire $OUTPUT_DIR/info/<stars>
        os.makedirs(graphs_path_stars, exist_ok=True) # creation du repertoire $OUTPUT_DIR/graphs/<stars> s'il n'existe pas
        for json_info in os.listdir(info_path_stars): # pour chaque fichier json dans $OUTPUT_DIR/info/<stars>
            load_graph_from_json(os.path.join(info_path_stars, json_info), graphs_path_stars) # chargement du graphe a partir du fichier json et sauvegarde dans $OUTPUT_DIR/graphs/<stars>/<repo_hash>

if __name__ == "__main__":
    get_graphs()