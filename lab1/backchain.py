from production import AND, OR, NOT, PASS, FAIL, IF, THEN, \
    match, populate, simplify, variables
from zookeeper import ZOOKEEPER_RULES


# This function, which you need to write, takes in a hypothesis
# that can be determined using a set of rules, and outputs a goal
# tree of which statements it would need to test to prove that
# hypothesis. Refer to the problem set (section 2) for more
# detailed specifications and examples.

# Note that this function is supposed to be a general
# backchainer.  You should not hard-code anything that is
# specific to a particular rule set.  The backchainer will be
# tested on things other than ZOOKEEPER_RULES.


def backchain_to_goal_tree(rules, hypothesis):
    tree = OR(hypothesis)
    for rule in rules:
        for outcome in rule.consequent():
            the_dict = match(outcome, hypothesis)
            # consequent not matched
            if the_dict is None:
                continue
            for i, antecedent in enumerate(rule.antecedent()):
                # if antecedent a string and not a RuleExpression
                if isinstance(rule.antecedent(), str):
                    antecedent = rule.antecedent()
                # recursion to get subtrees
                subtree = backchain_to_goal_tree(rules, populate(antecedent, the_dict))
                # AND node
                if isinstance(rule.antecedent(), AND) and len(rule.antecedent()) > 1:
                    # check if first leaf in original AND, add first and node
                    if i == 0:
                        tree.append(AND(subtree))
                    # if not first leaf in original AND node,
                    # add to existing AND node (which is at the end)
                    else:
                        tree[-1].append(AND(subtree))

                # OR node
                else:
                    tree.append(subtree)

    return simplify(tree)


# Here's an example of running the backward chainer - uncomment
# it to see it work:
# print backchain_to_goal_tree(ZOOKEEPER_RULES, 'opus is a penguin')
