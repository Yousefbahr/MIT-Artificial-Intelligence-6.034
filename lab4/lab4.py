from classify import *
import math

##
## CSP portion of lab 4.
##
from csp import BinaryConstraint, CSP, CSPState, Variable,\
    basic_constraint_checker, solve_csp_problem

# Implement basic forward checking on the CSPState see csp.py
def forward_checking(state, verbose=False):
    # Before running Forward checking we must ensure
    # that constraints are okay for this state.
    basic = basic_constraint_checker(state, verbose)
    # Return false if 'basic' return false
    if not basic:
        return False

    # Add your forward checking logic here.
    result = True
    var = state.get_current_variable()
    if var is not None:
        current_value = var.get_assigned_value()
    else:
        return result

    for constraint in state.get_all_constraints():

        if result is False:
            break

        var_i = state.get_variable_by_name(constraint.get_variable_i_name())
        next_variable = state.get_variable_by_name(constraint.get_variable_j_name())

        # when var_i is assigned and next_variable is not assigned
        if not (var_i.is_assigned() and not next_variable.is_assigned()) \
                or var_i != state.get_current_variable():
            continue

        # check all values of the variable
        for value in next_variable.get_domain():
            if not constraint.check(state=state, value_i=current_value, value_j=value):
                next_variable.reduce_domain(value)

        if len(next_variable.get_domain()) == 0:
            result = False

    return result
    # raise NotImplementedError

# Now Implement forward checking + (constraint) propagation through
# singleton domains.
def forward_checking_prop_singleton(state, verbose=False):
    # Run forward checking first.
    fc_checker = forward_checking(state, verbose)
    if not fc_checker:
        return False

    # Add your propagate singleton logic here.
    singleton_variables = []
    result = True

    if state.get_current_variable() is None:
        return result

    # get all singleton-domain variables
    for variable in state.get_all_variables():
        if variable.domain_size() == 1 and not variable.is_assigned():
            singleton_variables.append(variable)

    if len(singleton_variables) == 0:
        return result

    for variable in singleton_variables:
        for constraint in state.get_all_constraints():
            # if there is empty domain
            if result is False:
                break

            # get variable names
            var_i = state.get_variable_by_name(constraint.get_variable_i_name())
            next_variable = state.get_variable_by_name(constraint.get_variable_j_name())
            value_of_singleton = var_i.get_domain()[0]

            # both variables must be not assigned
            if not (not var_i.is_assigned() and not next_variable.is_assigned())\
                    or var_i != variable:
                continue

            # check all values of the variable
            for value in next_variable.get_domain():
                if not constraint.check(state=state, value_i=value_of_singleton, value_j=value):
                    next_variable.reduce_domain(value)

            # empty domain -> exit immediately
            if len(next_variable.get_domain()) == 0:
                result = False

            # add new singleton-domain variables
            if len(next_variable.get_domain()) == 1 and next_variable not in singleton_variables:
                singleton_variables.append(next_variable)

    return result
    # raise NotImplementedError

## The code here are for the tester
## Do not change.
from moose_csp import moose_csp_problem
from map_coloring_csp import map_coloring_csp_problem

def csp_solver_tree(problem, checker):
    problem_func = globals()[problem]
    checker_func = globals()[checker]
    answer, search_tree = problem_func().solve(checker_func)
    return search_tree.tree_to_string(search_tree)

##
## CODE for the learning portion of lab 4.
##

### Data sets for the lab
## You will be classifying data from these sets.
senate_people = read_congress_data('S110.ord')
senate_votes = read_vote_data('S110desc.csv')

house_people = read_congress_data('H110.ord')
house_votes = read_vote_data('H110desc.csv')

last_senate_people = read_congress_data('S109.ord')
last_senate_votes = read_vote_data('S109desc.csv')


### Part 1: Nearest Neighbors
## An example of evaluating a nearest-neighbors classifier.
senate_group1, senate_group2 = crosscheck_groups(senate_people)
# evaluate(nearest_neighbors(hamming_distance, 1), senate_group1, senate_group2, verbose=1)
## Write the euclidean_distance function.
## This function should take two lists of integers and
## find the Euclidean distance between them.
## See 'hamming_distance()' in classify.py for an example that
## computes Hamming distances.

def euclidean_distance(list1, list2):
    assert isinstance(list1, list)
    assert isinstance(list2, list)
    dist = 0
    for item1, item2 in zip(list1, list2):
        dist += (item2 - item1) ** 2

    return dist ** 0.5

#Once you have implemented euclidean_distance, you can check the results:
# evaluate(nearest_neighbors(euclidean_distance, 1), senate_group1, senate_group2, verbose=1)

## By changing the parameters you used, you can get a classifier factory that
## deals better with independents. Make a classifier that makes at most 3
## errors on the Senate.

my_classifier = nearest_neighbors(hamming_distance, 3)
# evaluate(my_classifier, senate_group1, senate_group2, verbose=1)

### Part 2: ID Trees
# print CongressIDTree(senate_people, senate_votes, homogeneous_disorder)

## Now write an information_disorder function to replace homogeneous_disorder,
## which should lead to simpler trees.

def information_disorder(yes, no):
    democrats = 0
    repub = 0
    for senator in yes:
        if senator == "Democrat":
            democrats += 1
        elif senator == "Republican":
            repub += 1

    if democrats == 0 or repub == 0:
        branch1 = 0
    else:
        branch1 = -((float(democrats) / len(yes)) * math.log(float(democrats) / len(yes),2) +
                    (float(repub) / len(yes)) * math.log(float(repub) / len(yes),2))

    democrats = 0
    repub = 0
    for senator in no:
        if senator == "Democrat":
            democrats += 1
        elif senator == "Republican":
            repub += 1

    if democrats == 0 or repub == 0:
        branch2 = 0
    else:
        branch2 = -((float(democrats) / len(no)) * math.log(float(democrats) / len(no),2) +
                    (float(repub) / len(no)) * math.log(float(repub) / len(no),2))

    return float(len(yes)) / len(yes + no) * branch1 + float(len(no)) / len(yes + no) * branch2


#print CongressIDTree(senate_people, senate_votes, information_disorder)
#evaluate(idtree_maker(senate_votes, homogeneous_disorder), senate_group1, senate_group2)

## Now try it on the House of Representatives. However, do it over a data set
## that only includes the most recent n votes, to show that it is possible to
## classify politicians without ludicrous amounts of information.

def limited_house_classifier(house_people, house_votes, n, verbose = False):
    house_limited, house_limited_votes = limit_votes(house_people,
    house_votes, n)
    house_limited_group1, house_limited_group2 = crosscheck_groups(house_limited)

    if verbose:
        print "ID tree for first group:"
        print CongressIDTree(house_limited_group1, house_limited_votes,
                             information_disorder)
        print
        print "ID tree for second group:"
        print CongressIDTree(house_limited_group2, house_limited_votes,
                             information_disorder)
        print
        
    return evaluate(idtree_maker(house_limited_votes, information_disorder),
                    house_limited_group1, house_limited_group2)

                                   
## Find a value of n that classifies at least 430 representatives correctly.
## Hint: It's not 10.
N_1 = 272
rep_classified = limited_house_classifier(house_people, house_votes, N_1)

## Find a value of n that classifies at least 90 senators correctly.
N_2 = 100
senator_classified = limited_house_classifier(senate_people, senate_votes, N_2)

## Now, find a value of n that classifies at least 95 of last year's senators correctly.
N_3 = 100
old_senator_classified = limited_house_classifier(last_senate_people, last_senate_votes, N_3)


## The standard survey questions.
HOW_MANY_HOURS_THIS_PSET_TOOK = ""
WHAT_I_FOUND_INTERESTING = ""
WHAT_I_FOUND_BORING = ""


## This function is used by the tester, please don't modify it!
def eval_test(eval_fn, group1, group2, verbose = 0):
    """ Find eval_fn in globals(), then execute evaluate() on it """
    # Only allow known-safe eval_fn's
    if eval_fn in [ 'my_classifier' ]:
        return evaluate(globals()[eval_fn], group1, group2, verbose)
    else:
        raise Exception, "Error: Tester tried to use an invalid evaluation function: '%s'" % eval_fn

    
