import subprocess
import os
import json
import git
import networkx as nx

OUTPUT_DIR = "dossiers_git"

def save_graph(file_path, graph):
    with open(file_path, 'wb') as f:
        nx.write_edgelist(graph, f, data=False)

def load_json(file_path)->dict:
    with open(file_path) as f:
        return json.load(f)

def process_repository(repo_path, output_file_path):
    repo = git.Repo(repo_path)
    
    g = {}

    for commit in repo.iter_commits('--all'):
        commit_hash = str(commit)
        parents = [str(parent) for parent in commit.parents]

        if commit_hash not in g:
            g[commit_hash] = set()
        g[commit_hash].update(parents)

    repo.close()

    graph = nx.DiGraph(g)
    save_graph(output_file_path, graph)

def load_graph_from_json(file_path, out_dir):
    file = load_json(file_path)
    subprocess.run(["git", "clone", file["clone_url"]], check=True)
    process_repository(file["name"], os.path.join(out_dir, str(file["id"])))
    os.system('rmdir /S /Q "{}"'.format(file["name"]))

def get_graphs():
    print("Récupération des graphes...")

    info_path = os.path.join(OUTPUT_DIR, "info")
    graphs_path = os.path.join(OUTPUT_DIR, "graphs")
    info_star_folders = [f for f in os.listdir(info_path) if os.path.isdir(os.path.join(info_path, f))]

    for folder_name in info_star_folders:
        graphs_path_stars = os.path.join(graphs_path, folder_name)
        info_path_stars = os.path.join(info_path, folder_name)
        os.makedirs(graphs_path_stars, exist_ok=True)
        for json_info in os.listdir(info_path_stars):
            load_graph_from_json(os.path.join(info_path_stars, json_info), graphs_path_stars)

if __name__ == "__main__":
    get_graphs()