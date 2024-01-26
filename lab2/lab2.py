# Fall 2012 6.034 Lab 2: Search
#
# Your answers for the true and false questions will be in the following form.  
# Your answers will look like one of the two below:
# ANSWER1 = True
# ANSWER1 = False

# 1: True or false - Hill Climbing search is guaranteed to find a solution
#    if there is a solution
ANSWER1 = False

# 2: True or false - Best-first search will give an optimal search result
#    (shortest path length).
#    (If you don't know what we mean by best-first search, refer to
#     http://courses.csail.mit.edu/6.034f/ai3/ch4.pdf (page 13 of the pdf).)
ANSWER2 = False

# 3: True or false - Best-first search and hill climbing make use of
#    heuristic values of nodes.
ANSWER3 = True

# 4: True or false - A* uses an extended-nodes set.
ANSWER4 = True

# 5: True or false - Breadth first search is guaranteed to return a path
#    with the shortest number of nodes.
ANSWER5 = True

# 6: True or false - The regular branch and bound uses heuristic values
#    to speed up the search for an optimal path.
ANSWER6 = False

# Import the Graph data structure from 'search.py'
# Refer to search.py for documentation
from search import Graph

## Optional Warm-up: BFS and DFS
# If you implement these, the offline tester will test them.
# If you don't, it won't.
# The online tester will not test them.


def bfs(graph, start, goal):
    agenda = [[start]]
    extended_set = set()

    while True:
        path = agenda.pop(0)

        # The node to be extended
        start = path[-1]

        # add the extended node to extended set
        extended_set.add(start)

        if start == goal:
            return path

        # extend nodes and append to agenda
        for i, node in enumerate(graph.get_connected_nodes(start)):
            # insert into agenda if node never extended before
            if node not in extended_set:
                agenda.append(path + [node])

    return []


## Once you have completed the breadth-first search,
## this part should be very simple to complete.

def dfs(graph, start, goal):
    agenda = [[start]]
    extended_set = set()

    while len(agenda) > 0:

        path = agenda.pop(0)

        # The node to be extended
        start = path[-1]

        # add the extended node to extended set
        extended_set.add(start)

        # check for goal
        if start == goal:
            return path

        # extend nodes and append to agenda
        for node in graph.get_connected_nodes(start):
            # insert into agenda if node never extended before
            if node not in extended_set:
                agenda.insert(0, path + [node])

    return []


## Now we're going to add some heuristics into the search.
## Remember that hill-climbing is a modified version of depth-first search.
## Search direction should be towards lower heuristic values to the goal.


def hill_climbing(graph, start, goal):
    agenda = [[start]]

    while len(agenda) != 0:
        path = agenda.pop(0)

        # The node to be extended
        start = path[-1]

        # check for goal
        if start == goal:
            return path

        # extend nodes and append to agenda
        for node in graph.get_connected_nodes(start):
            # # insert into agenda
            if node not in path:
                agenda.append(path + [node])

        # sort the agenda based on levels of depth first, then heuristics
        # get longest depth
        longest = max(len(elem) for elem in agenda)

        # sort by levels of depth
        agenda = sorted(agenda, key=lambda my_path: len(my_path), reverse=True)

        # get index of first element which is not of the longest length
        # exclude those elements from next level of sorting (by heuristics)
        index = [i for i, elem in enumerate(agenda) if len(elem) != longest]
        index = len(agenda) if len(index) == 0 else index[0]

        agenda = sorted(agenda[:index], key=lambda my_path: graph.get_heuristic(my_path[-1], goal)) + agenda[index:]

    return []


## Now we're going to implement beam search, a variation on BFS
## that caps the amount of memory used to store paths.  Remember,
## we maintain only k candidate paths of length n in our agenda at any time.
## The k top candidates are to be determined using the 
## graph get_heuristic function, with lower values being better values.

def beam_search(graph, start, goal, beam_width):
    agenda = [[start]]
    while True:
        same_level = True

        path = agenda.pop(0)

        # The node to be extended
        start = path[-1]

        # check for goal
        if start == goal:
            return path

        # extend nodes and append to agenda
        for node in graph.get_connected_nodes(start):
            # # insert into agenda
            if node not in path:
                agenda.append(path + [node])

        # No more paths
        if len(agenda) == 0:
            break

        # Check if all paths at same level
        path_level = len(agenda[0])
        for path in agenda:
            if len(path) != path_level:
                same_level = False
                break

        # Paths of same length
        if same_level:
            agenda = sorted(agenda, key=lambda my_path: graph.get_heuristic(my_path[-1], goal))[:beam_width]
        # paths of different lengths
        # extend the shortest path to make all paths at the  same level
        else:
            agenda = sorted(agenda, key=lambda my_path: len(my_path))

    return []


## Now we're going to try optimal search.  The previous searches haven't
## used edge distances in the calculation.

## This function takes in a graph and a list of node names, and returns
## the sum of edge lengths along the path -- the total distance in the path.
def path_length(graph, node_names):
    count = 0
    for node1, node2 in zip(node_names, node_names[1:]):
        if graph.get_edge(node1, node2):
            count += graph.get_edge(node1, node2).length

    return count


def branch_and_bound(graph, start, goal):
    agenda = [[start]]
    while len(agenda) != 0:
        path = agenda.pop(0)

        start = path[-1]

        if start == goal:
            return path

        for node in graph.get_connected_nodes(start):
            if node not in path:
                agenda.append(path + [node])

        agenda = sorted(agenda, key=lambda my_path: path_length(graph, my_path))

    return []


def a_star(graph, start, goal):
    agenda = [[start]]
    extended_set = set()

    while len(agenda) != 0:
        path = agenda.pop(0)

        start = path[-1]
        extended_set.add(start)

        if start == goal:
            return path

        for node in graph.get_connected_nodes(start):
            if node not in extended_set:
                agenda.append(path + [node])

        agenda = sorted(agenda, key=lambda my_path: path_length(graph, my_path) +
                                                            graph.get_heuristic(my_path[-1], goal))

    return []


## It's useful to determine if a graph has a consistent and admissible
## heuristic.  You've seen graphs with heuristics that are
## admissible, but not consistent.  Have you seen any graphs that are
## consistent, but not admissible?

def is_admissible(graph, goal):
    for node in graph.nodes:
        shortest_path = a_star(graph, node, goal)
        if not graph.get_heuristic(node, goal) <= path_length(graph,shortest_path):
            return False

    return True

def is_consistent(graph, goal):
    for edge in graph.edges:
        if not edge.length >= abs(graph.get_heuristic(edge.node1, goal) - graph.get_heuristic(edge.node2, goal)):
            return False

    return True

HOW_MANY_HOURS_THIS_PSET_TOOK = ' '
WHAT_I_FOUND_INTERESTING = ' '
WHAT_I_FOUND_BORING = ' '
