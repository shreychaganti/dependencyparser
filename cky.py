"""
COMS W4705 - Natural Language Processing - Fall 2019
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True


class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar):
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self, tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        n = len(tokens)
        lhs = self.grammar.lhs_to_rules
        ds = defaultdict(dict)
        lhs_keys = list(lhs.keys())
        rhs = self.grammar.rhs_to_rules
        rhs_keys = list(rhs.keys())

        r = len(lhs_keys)

        for i in range(n):
            nt = rhs[(tokens[i],)]
            print(nt)
            for rule in nt:
                ds[(i, i + 1)][rule[0]] = 1

        # print(ds)

        for l in range(2, n + 1):
            for i in range(n - l + 1):
                j = i + l
                for k in range(i + 1, j):
                    B = ds[(i, k)]
                    C = ds[(k, j)]
                    # print(B)
                    for t1 in B.keys():
                        for t2 in C.keys():
                            rules = rhs[(tuple((t1, t2)))]
                            for rule in rules:
                                ds[(i, j)][rule[0]] = 1

        print(ds)

        if len(ds[(0, n)].keys()) > 0:
            return True

        return False

    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        # table= None
        probs = defaultdict(dict)

        n = len(tokens)
        lhs = self.grammar.lhs_to_rules
        ds = defaultdict(dict)
        lhs_keys = list(lhs.keys())
        rhs = self.grammar.rhs_to_rules
        rhs_keys = list(rhs.keys())

        r = len(lhs_keys)

        for i in range(n):
            nonterminals = rhs[(tokens[i],)]
            print(nonterminals)
            for rule in nonterminals:
                ds[(i, i + 1)][rule[0]] = str(tokens[i])
                probs[(i, i + 1)][rule[0]] = math.log(rule[2])

        # print(ds)

        for l in range(2, n + 1):
            for i in range(n - l + 1):
                j = i + l
                for k in range(i + 1, j):

                    B = ds[(i, k)]
                    C = ds[(k, j)]

                    for t1 in B.keys():
                        for t2 in C.keys():
                            rules = rhs[(tuple((t1, t2)))]
                            prob_b = probs[(i, k)][t1]
                            prob_c = probs[(k, j)][t2]

                            for rule in rules:
                                prob_a = math.log(rule[2])

                                prob_temp = prob_a + prob_b + prob_c

                                if (rule[0] not in ds[(i, j)].keys()) or (probs[(i, j)][rule[0]] < prob_temp):
                                    ds[(i, j)][rule[0]] = ((t1, i, k), (t2, k, j))
                                    probs[(i, j)][rule[0]] = prob_temp

        # print(ds)

        return ds, probs


def get_tree(chart, i, j, nt):
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
    if type(chart[(i, j)][nt]) is str:
        return (nt, chart[(i, j)][nt])

    elif len(chart[(i, j)][nt]) == 2:
        l = chart[(i, j)][nt][0]
        r = chart[(i, j)][nt][1]
        tree_l = get_tree(chart, l[1], l[2], l[0])
        tree_r = get_tree(chart, r[1], r[2], r[0])

    return (nt, tree_l, tree_r)


if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        #print(parser.is_in_language(toks))
        #table,probs = parser.parse_with_backpointers(toks)
        #assert check_table_format(chart)
        #assert check_probs_format(probs)
        
