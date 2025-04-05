import os
import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import copy

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
        self.name+=" / "+l2.name
        for i,stars in enumerate(l2):
            for j,e in enumerate(stars):
                self.l[i][j]/=e
        return self
    
    def mul(self, l2):
        self.name+=" * "+l2.name

        for i,stars in enumerate(l2):
            for j,e in enumerate(stars):
                self.l[i][j]*=e
        return self

    def add(self, l2):
        self.name+=" + "+l2.name

        for i,stars in enumerate(l2):
            for j,e in enumerate(stars):
                self.l[i][j]+=e
        return self

    def sub(self, l2):
        self.name+=" - "+l2.name

        for i,stars in enumerate(l2):
            for j,e in enumerate(stars):
                self.l[i][j]-=e
        return self
                
    def mulConst(self, v):
        self.name=str(round(v, 3))+" * "+self.name

        for i in range(len(self.l)):
            for j in range(len(self.l[i])):
                self.l[i][j] *= v
        return self

    def max(self):
        #self.name = "norm("+self.name+")"
        return max(max(row) for row in self.l)
    
    def normalize(self):
        return self.mulConst(1/self.max())


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
    
    def mulConst(self, v):
        for i in range(len(self.l)):
            self.l[i] *= v
        return self

    def max(self):
        return max(self.l)

    def normalize(self):
        return self.mulConst(1/self.max())

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
        num_bars = len(l[0])
    
        group_width = 0.8
        x_positions = np.arange(len(l))
    
        bar_width = group_width / num_bars
    
        colors = plt.cm.get_cmap('tab10', len(l))
    
        for i, group in enumerate(l):
            for j, value in enumerate(group):
                group_color = colors(j)
                
                if i==0:
                    if(len(l.labels) == 0):
                        plt.bar(x_positions[i] + j * bar_width, value, width=bar_width, color=group_color, label=str(j))
                    else:
                        plt.bar(x_positions[i] + j * bar_width, value, width=bar_width, color=group_color, label=l.labels[j])
                else:
                    plt.bar(x_positions[i] + j * bar_width, value, width=bar_width, color=group_color)
    
        plt.xticks(x_positions + (group_width / 2) - (bar_width / 2), self.stars_folders)
    
        plt.xlabel('stars')
        plt.ylabel(l.name)
        plt.title(name)
        plt.legend()
        plt.show()
    
    def get_by_stars(self, func):
        '''
        nb_commit
        nb_merge
        degree_entrant
        degree_sortant
        degree_total
        '''
        l = MultipleValueList(name=func.__name__)
        for folder in self.stars_folders:
            val = ValueList()
            for repo in self.__get_repos_for_stars(folder):
                g = self.__load_graph(os.path.join(self.graphs_folder, folder, repo))
                res = func(g)
                if(len(val)<len(res)):
                    val.l += [0]*(len(res)-len(val))
                val.add(res)
            l.append(val.l)
        return l

    def __get_repos_for_stars(self, stars:str)->list[str]:
        return [f for f in os.listdir(os.path.join(self.graphs_folder, stars))]
    
    def __load_graph(self, file_path:str):
        graph = nx.read_edgelist(file_path, create_using=nx.DiGraph())
        return graph

    def degree_entrant(self, G, normalize:bool = False):
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

    def degree_sortant(self, G, normalize:bool = False):
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

    def degree_total(self, G, normalize:bool = False):
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

    def nb_merge(self, G):
        c = 0
        for node in G.nodes:
            if len(list(G.predecessors(node))) > 1:
                c+=1
        return ValueList([c])

    def nb_commit(self, G):
        return ValueList([G.number_of_nodes()])