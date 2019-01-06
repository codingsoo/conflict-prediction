"""
    @file   python_floyd.py
    @brief
        Floyd-Warshall Algorithm
        To calculate the distance for the dependency.

"""

import queue

adjacency_matrix = dict()

def load_graph( edge_lists ) :
    for u, v in edge_lists :
        if not u in adjacency_matrix :
            adjacency_matrix[u] = dict()
        adjacency_matrix[u][v] = 1

def run_floyd() :
    for logic in adjacency_matrix.keys() :
        pq = queue.PriorityQueue()
        pq.put([0, logic])
        visited_set = set()
        dist_dict = adjacency_matrix[logic]
        adjacency_matrix[logic][logic] = 0
        while not pq.empty() :
            cur_value, cur_logic = pq.get()
            if cur_logic in visited_set :
                continue
            visited_set.add(cur_logic)
            for next_logic, value in adjacency_matrix.get(cur_logic, dict()).items():
                if not next_logic in visited_set :
                    if dist_dict.get(next_logic, cur_value + value + 1) >= cur_value + value :
                        dist_dict[next_logic] = cur_value + value
                        pq.put([cur_value + value, next_logic])

def save_result() :
    ret_list = []
    for key1, value1 in  adjacency_matrix.items() :
        for key2, value2  in value1.items() :
            ret_list.append([key1, key2, value2])
    return ret_list

def create_indirect_edge_list( edge_lists ) :
    adjacency_matrix = dict()
    load_graph( edge_lists )
    run_floyd()
    return save_result()