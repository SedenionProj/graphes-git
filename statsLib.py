import os
import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import copy
import pickle
from networkx import DiGraph
from queue import Queue

class __List:
    def __init__(self):
        self.l = []

    def __getitem__(self, index):
        return self.l[index]

    def __setitem__(self, index, value):
        self.l[index] = value

    def __len__(self):
        return len(self.l)

    def __iter__(self):
        return iter(self.l)

    def append(self, value):
        self.l.append(value)

class MultipleValueList(__List):
    def __init__(self, name:str = "value", labels:list[str]= [], l:list = []):
        self.l = copy.deepcopy(l)
        self.labels = labels
        self.name = name
    
    def div(self, l2):
        self.name ="("+self.name+" / "+l2.name+")"
        for i,stars in enumerate(l2):
            for j,e in enumerate(stars):
                self.l[i][j]/=e
        return self
    
    def mul(self, l2):
        self.name ="("+self.name+" * "+l2.name+")"

        for i,stars in enumerate(l2):
            for j,e in enumerate(stars):
                self.l[i][j]*=e
        return self

    def add(self, l2):
        self.name+="("+self.name+" + "+l2.name+")"

        for i,stars in enumerate(l2):
            for j,e in enumerate(stars):
                self.l[i][j]+=e
        return self

    def sub(self, l2):
        self.name= "("+self.name+" - "+l2.name+")"

        for i,stars in enumerate(l2):
            for j,e in enumerate(stars):
                self.l[i][j]-=e
        return self
                
    def mul_const(self, v):
        self.name= "("+str(round(v, 3))+" * "+self.name+")"

        for i in range(len(self.l)):
            for j in range(len(self.l[i])):
                self.l[i][j] *= v
        return self

    def max(self):
        self.name = "max("+self.name+")" # jsp
        return max(max(row) for row in self.l)
    
    def normalize(self):
        v = 1/self.max()
        self.name= "normalize("+self.name+")"

        for i in range(len(self.l)):
            for j in range(len(self.l[i])):
                self.l[i][j] *= v
        return self
    
    def extend_by(self, n:int, v:int = None):
        for i in range(len(self.l)):
            print(self.l[i], [self.l[i][len(self.l[i])-1]]*n)
            if v is None:
                self.l[i] += [self.l[i][len(self.l[i])-1]]*n
            else:
                self.l[i] += [v]*n
        return self
    
    def get_sub_list(self, i:int):
        return MultipleValueList(
            name=self.name + f"[{i}]",
            l=[[stars[i] if i < len(stars) else 0] for stars in self.l]
        )
    
    def average_by_stars(self):
        self.name= "average_by_stars("+self.name+")"
        for i in range(len(self.l)): # pour chaque forchette d'étoiles
            s = sum(self.l[i]) # somme des valeurs de la forchette d'étoiles
            print(s)
            for j in range(len(self.l[i])): 
                self.l[i][j]/=s # moyenne des valeurs de la forchette d'étoiles
        return self


class ValueList(__List):
    def __init__(self, l:list[int] = []):
        self.l = copy.deepcopy(l)

    def div(self, l2):
        for i,e in enumerate(l2):
            self.l[i]/=e
        return self
    
    def mul(self, l2):
        for i,e in enumerate(l2):
            self.l[i]*=e
        return self

    def add(self, l2):
        for i,e in enumerate(l2):
            self.l[i]+=e
        return self

    def sub(self, l2):
        for i,e in enumerate(l2):
            self.l[i]-=e
        return self
    
    def mul_const(self, v):
        for i in range(len(self.l)):
            self.l[i] *= v
        return self

    def max(self):
        return max(self.l)

    def normalize(self):
        return self.mul_const(1/self.max())

class Stats:
    def __init__(self, folder_path:str):
        graphs_path = os.path.join(folder_path, "graphs")
        stars_folders = [f for f in os.listdir(graphs_path) if os.path.isdir(os.path.join(graphs_path, f))]
        stars_folders.sort(key = lambda x: int(x.split("-")[0]))
        self.stars_folders = stars_folders;
        self.graphs_folder = os.path.join(folder_path, "graphs")
        self.info_folder = os.path.join(folder_path, "info")
    
    def get_infos_by_stars(self, name:str)->ValueList:
        '''
        forks_count         : nombre de forks
        open_issues_count   : nombre d'issues
        size                : taille en Ko
        stargazers_count    : nombre d'étoiles
        '''
        l = MultipleValueList(name)
        for folder in self.stars_folders:
            val = 0
            for repo in self.__get_repos_for_stars(folder):
                with open(os.path.join(self.info_folder, folder, repo+".json"), 'r') as f:
                    data = json.load(f)
                    val += data[name]
            l.append([val])
        return l
    
    def show_chart_by_stars(self, l:MultipleValueList, name:str = "chart"):
        num_bars = max(len(l[i]) for i in range(len(l)))
        group_width = 0.8
        x_positions = np.arange(len(l))
    
        bar_width = group_width / num_bars
    
        colors = plt.cm.get_cmap(lut= num_bars)
        
        plt.figure(figsize=(12, 6))

        labels_visite = []

        for i, group in enumerate(l):
            for j, value in enumerate(group):
                group_color = colors(j)
                
                if j not in labels_visite:
                    labels_visite.append(j)
                    if len(group)==1:
                        plt.bar(x_positions[i] + j * bar_width, value, width=bar_width, color=group_color)
                    elif len(l.labels) == 0:
                        plt.bar(x_positions[i] + j * bar_width, value, width=bar_width, color=group_color, label=str(j))
                    else:
                        plt.bar(x_positions[i] + j * bar_width, value, width=bar_width, color=group_color, label=l.labels[j])
                else:
                    plt.bar(x_positions[i] + j * bar_width, value, width=bar_width, color=group_color)
    
        plt.xticks(x_positions + (group_width / 2) - (bar_width / 2), self.stars_folders)
    
        plt.xlabel("fourchettes d'etoiles")
        plt.ylabel(l.name)
        #plt.title(name)
        plt.legend()
        plt.show()
    
    def show_multiple_charts_by_stars(self, *lists):
        num_bars = len(lists)
    
        group_width = 0.8
        x_positions = np.arange(len(lists[0]))
    
        bar_width = group_width / num_bars
    
        colors = plt.cm.get_cmap(lut= num_bars)
        
        plt.figure(figsize=(12, 6))

        for j, group in enumerate(lists):
            for i, value in enumerate(group):

                group_color = colors(j)
                
                if i==0:
                    plt.bar(x_positions[i] + j * bar_width, value, width=bar_width, color=group_color, label=lists[j].name)
                else:
                    plt.bar(x_positions[i] + j * bar_width, value, width=bar_width, color=group_color)

        plt.xticks(x_positions + (group_width / 2) - (bar_width / 2), self.stars_folders)
        plt.xlabel("fourchettes d'etoiles")
        plt.ylabel("valeurs")
        #plt.title('charts')
        plt.legend()
        plt.show()

    def get_by_stars(self, func, *args):
        '''
        nb_commit
        nb_merges
        nb_merges_diff_auteurs
        nb_edges
        nb_motifs (param : Graphe, nom)
        largeur
        degree_entrant
        degree_sortant
        degree_total
        connexe
        '''
        l = MultipleValueList(name=func.__name__)
        for folder in self.stars_folders:
            val = ValueList()
            for repo in self.__get_repos_for_stars(folder):
                g = self.__load_graph(os.path.join(self.graphs_folder, folder, repo))
                if args:
                    res = func(g, args[0])
                    l.name = func.__name__+" \""+str(args[1])+"\""
                else:
                    res = func(g)
                if(len(val)<len(res)):
                    val.l += [0]*(len(res)-len(val))
                val.add(res)
            l.append(val.l)
        return l

    def __get_repos_for_stars(self, stars:str)->list[str]:
        return [f for f in os.listdir(os.path.join(self.graphs_folder, stars))]
    
    def __load_graph(self, file_path:str):
        with open(file_path, 'rb') as f:
            graph = pickle.load(f)
        return graph

    def degree_entrant(self, G:DiGraph, normalize:bool = False):
        vals = dict(G.in_degree()).values()
        m = max(vals)
        L = [0]*(m+1)
        for val in vals:
            L[val]+=1

        if normalize:
            s=sum(L)
            for i in range(m):
                L[i]/=s

        return ValueList(L)

    def degree_sortant(self, G:DiGraph, normalize:bool = False):
        vals = dict(G.out_degree()).values()
        m = max(vals)
        L = [0]*(m+1)
        for val in vals:
            L[val]+=1

        if normalize:
            s=sum(L)
            for i in range(m):
                L[i]/=s

        return ValueList(L)

    def degree_total(self, G:DiGraph, normalize:bool = False):
        vals = dict(G.degree()).values()
        m = max(vals)
        L = [0]*(m+1)
        for val in vals:
            L[val]+=1

        if normalize:
            s=sum(L)
            for i in range(m):
                L[i]/=s

        return ValueList(L)

    def nb_merges(self, G:DiGraph):
        c = 0
        for _, node in G.nodes(data=True):
            if node.get("color", "gray") != "lightblue":
                c+=1
        return ValueList([c])
    
    def nb_merges_diff_auteurs(self, G:DiGraph):
        c = 0
        for _, node in G.nodes(data=True):
            if node.get("color", "gray") == "orange":
                c+=1
        return ValueList([c])

    def nb_commit(self, G:DiGraph):
        return ValueList([G.number_of_nodes()])
    
    def nb_edges(self, G:DiGraph):
        return ValueList([G.number_of_edges()])
    
    def largeur(self, G:DiGraph):
        no_predecessors = [n for n in G.nodes if G.in_degree(n) == 0]

        def max_parcours_largeur(s):
            visite_dist = {}
            f = Queue()
            f.put(s)
            visite_dist[s] = 0

            while not f.empty():
                s = f.get()
                dist = visite_dist[s]
                for succ in G.successors(s):
                    if not succ in visite_dist.keys():
                        f.put(succ)
                        visite_dist[succ] = dist+1

            compteur = {}
            for val in visite_dist.values():
                compteur[val] = compteur.get(val, 0) + 1

            return max(compteur.values())
    
        return ValueList([max([max_parcours_largeur(s) for s in no_predecessors])])

    def connexe(self, G:DiGraph):
        return ValueList([nx.is_weakly_connected(G)])

    def nb_motifs(self, G:DiGraph, H:DiGraph):
        matcher = nx.algorithms.isomorphism.DiGraphMatcher(G, H)
        res = sum(1 for _ in matcher.subgraph_isomorphisms_iter())
        return ValueList([res])

    def show_infos(self):
        count = 0
        for folder in self.stars_folders:
            for repo in self.__get_repos_for_stars(folder):
                g = self.__load_graph(os.path.join(self.graphs_folder, folder, repo))
                print(folder+"/"+repo, "nb commit", self.nb_commit(g).l, "nb merges", self.nb_merges(g).l, "degree", self.degree_entrant(g).l)
                count += 1
        print("total",count)