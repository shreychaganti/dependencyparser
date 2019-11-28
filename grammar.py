
import sys
from collections import defaultdict
from math import fsum

class Pcfg(object):
    """
    Represent a probabilistic context free grammar.
    """

    def __init__(self, grammar_file):
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None
        self.read_rules(grammar_file)

    def read_rules(self,grammar_file):

        for line in grammar_file:
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line:
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else:
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()


    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1)
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False.
        """
        # TODO, Part 1
        for el in self.lhs_to_rules.keys():
            elements = self.lhs_to_rules[s]
            p = fsum(list(zip(*elements))[2])
            if (1-p) > .00001:
                return False

        for el in self.rhs_to_rules.keys():
            if len(el) > 2:
                return False
            elif len(el) == 1:
                if self.lhs_to_rules[el]:
                    return False

        return True


if __name__ == "__main__":
    #with open(sys.argv[1],'r') as grammar_file:
    with open('atis3.pcfg', 'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        
