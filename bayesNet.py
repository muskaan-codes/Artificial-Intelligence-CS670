import random


class Node:
    name = ""
    parentNames = []
    cpt = []

    def __init__(self, nodeInfo):
        """
        :param nodeInfo: in the format as [name, parents, cpt]
        """
        # name, parents, cpt

        self.name = nodeInfo[0]
        self.parentNames = nodeInfo[1].copy()
        self.cpt = nodeInfo[2].copy()

    def format_cpt(self):
        s_cpt = '\t'.join(self.parentNames) + '\n'
        for i in range(len(self.cpt)):
            s_cpt += bin(i).replace("0b", "").zfill(len(self.parentNames)).replace('0', 'T\t').replace('1', 'F\t')
            s_cpt += str(self.cpt[i]) + '\n'
        return s_cpt

    def print(self):
        print("name: {}\nparents:{}\ncpt:\n{}".format(self.name, self.parentNames, self.format_cpt()))


class BayesNet:
    nodes = []
    nodeValues = {}

    def __init__(self, nodeList):
        for n in nodeList:
            self.nodes.append(Node(n))
        for n in self.nodes:
            self.nodeValues[n.name] = None  # value of node

    def print(self):
        for n in self.nodes:
            n.print()

    def getNodeConditionalProbability(self, node):
        return node.cpt[0]

    def sampleNode(self, node):
        """sample value for a node given its cpt"""
        self.nodeValues[node.name] = True if random.random() <= self.getNodeConditionalProbability(node) else False

    def priorSample(self):
        """assigns new values to the nodes in the network by sampling from the joint distribution"""
        for n in self.nodes:
            #             print(n.name)
            self.sampleNode(n)

    def testModel(self, evidence):
        """
            return true if all the evidence variables in the
            network have the value specified by the evidence values
        """
        for key in evidence:
            if self.nodeValues[key] != evidence[key]:
                return False
        return True

    def rejectionSampling(self, qVar, evidence, N):
        """
            :param qVar: query variable
            :param evidence: evidence variables and their values in a dictionary
            :param N: maximum number of iterations
            E.g. ['WetGrass',{'Sprinkler':True, 'Rain':False}, 10000]
            :return: probability distribution for the query
        """
        counts = [0, 0]
        for i in range(N):
            self.priorSample()
            if self.testModel(evidence):
                if self.nodeValues[qVar]:
                    counts[0] += 1
                else:
                    counts[1] += 1
        prob = round(float(counts[0]) / float(counts[0] + counts[1]), 3)
        return [prob, round(1 - prob, 3)]

    def children(self, queryNode):
        """
        return a list of a node's children queryNode
        """
        children = []
        for n in self.nodes:
            if queryNode in n.parentNames and n not in children:
                children.append(n)
        return children

    def gibbsSampling(self, qVar, evidence, N):
        """
            :param qVar: query variable
            :param evidence: evidence variables and their values in a dictionary
            :param N: maximum number of iterations
            E.g. ['WetGrass',{'Sprinkler':True, 'Rain':False}, 10000]
            :return: probability distribution for the query
            3, [4, 5], [False, True], 10000)
        """
        counts = [0, 0]

        # Set evidence nodes
        for key in evidence:
            self.nodeValues[key] = evidence[key]

        # reference to query node
        for n in self.nodes:
            if n.name == qVar:
                q = n

        # non-evidence nodes.
        #         nonEvidence = [node for node in self.nodes if node.name not in evidence.keys()]
        nonEvidence = []
        for node in self.nodes:
            if node.name not in evidence.keys():
                nonEvidence.append(node)

        # children of the non-evidence nodes
        children = {}
        for node in nonEvidence:
            children[node] = self.children(node)

        # Randomly assign values to the non-evidence variables
        for n in nonEvidence:
            self.nodeValues[n.name] = True if random.random() <= 0.5 else False

        for i in range(N):
            # Increment count according latest state of query node
            if self.nodeValues[qVar]:
                counts[0] += 1
            else:
                counts[1] += 1

            for n in nonEvidence:
                # cpt --> P(X | Parents(X))
                P_true = self.getNodeConditionalProbability(n)
                P_false = 1.0 - P_true

                # cpt of child nodes given their parents
                for c in children[n]:
                    # P(c|n=true,OtherParents(c))
                    self.nodeValues[n.name] = True
                    pt = self.getNodeConditionalProbability(c)

                    # P(c|n=false,OtherParents(c))
                    self.nodeValues[n.name] = False
                    pf = self.getNodeConditionalProbability(c)

                    # If the node is false, 1-P
                    if self.nodeValues[c.name]:
                        P_true *= pt
                        P_false *= pf
                    else:
                        P_true *= (1.0 - pt)
                        P_false *= (1.0 - pf)

                # Normalise for true probability
                P = P_true / (P_true + P_false)

                # With P, set the value of the node to true
                self.nodeValues[n.name] = True if random.random() <= P else False

        # Normalise count for prob
        prob = round(float(counts[0]) / float(counts[0] + counts[1]), 3)
        return [prob, round(1 - prob, 3)]

# Sample Bayes net
nodes = [["Cloudy", [], [0.5]],
         ["Sprinkler", ["Cloudy"], [0.1, 0.5]],
         ["Rain", ["Cloudy"], [0.8, 0.2]],
         ["WetGrass", ["Sprinkler", "Rain"], [0.99, 0.9, 0.9, 0.0]]]
b = BayesNet(nodes)
b.print()

# Sample queries to test your code
print(b.gibbsSampling("Rain", {"Sprinkler": True, "WetGrass": False}, 100000))
print(b.rejectionSampling("Rain", {"Sprinkler": True}, 1000))
