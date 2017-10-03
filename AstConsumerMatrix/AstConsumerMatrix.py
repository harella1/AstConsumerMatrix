'''
Get all function calls from a python file

The MIT License (MIT)
Copyright (c) 2016 Suhas S G <jargnar@gmail.com>
'''
import ast
from collections import deque


class FuncCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self._name = deque()

    @property
    def name(self):
        return '.'.join(self._name)

    @name.deleter
    def name(self):
        self._name.clear()

    def visit_Name(self, node):
        self._name.appendleft(node.id)

    def visit_Attribute(self, node):
        try:
            self._name.appendleft(node.attr)
            self._name.appendleft(node.value.id)
        except AttributeError:
            self.generic_visit(node)


def get_func_calls(tree):
    class_calls = {}
    c = "main"
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            c = node.name
            class_calls[c] = []
            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    callvisitor = FuncCallVisitor()
                    callvisitor.visit(n.func)
                    class_calls[c].append(callvisitor.name)
        if isinstance(node, ast.Call):
            callvisitor = FuncCallVisitor()
            callvisitor.visit(node.func)
            class_calls[c].append(callvisitor.name)

    return class_calls


def output(calls):
    import numpy as np
    from matplotlib import pyplot as plt
    from matplotlib import gridspec as mtgs
    from matplotlib.backends.backend_pdf import PdfPages

    x = list(set(calls.keys()))
    y = list(set([item for sublist in calls.values() for item in sublist]))
    #Interfaces = np.zeros((len(y),len(x)), dtype=np.int)
    Dependencies = np.zeros((len(y),len(x)), dtype=np.int)
    for item,funcCalls in calls.items():
        for call in funcCalls:
         Dependencies[y.index(call),x.index(item)] = 1
    #for method,item in list(set(d[pattern].Dependencies)):
    #    if method in y and item in x:
    #        Dependencies[pattern][y.index(method),x.index(item)] = 1

    fig = plt.figure(figsize = (len(x),len(y)))
    fig.suptitle('Consumer', fontsize=14)           
    gs = mtgs.GridSpec(nrows=2,ncols=1,right=0.98)

    #vals = Interfaces*-100+300

    #ax1 = fig.add_subplot(gs[0])
    #ax1.axis('off')
    #ax1.set_title('Interfaces')
    #the_table = ax1.table(cellText=Interfaces[pattern], loc='center',cellLoc='center',rowLabels=y, colLabels=x,cellColours=plt.cm.hot(vals))
    ##[the_table._cells[(i,0)].set_width(0.1) for i in range(0,len(y))]
    
    vals = Dependencies*-100+300
    ax2 = fig.add_subplot(gs[1])
    ax2.axis('off')
    ax2.set_title('Dependencies')
    the_table = ax2.table(cellText=Dependencies, loc='center',cellLoc='center',rowLabels=y, colLabels=x,cellColours=plt.cm.hot(vals))
    #the_table.scale(1.5, 1.5)
    #fig.subplots_adjust(left=0.3),colWidths=[0.15]*len(y),colWidths=[0.15]*len(y)
    #plt.show()
    plt.savefig('Consumer.pdf',bbox_inches='tight')

    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input .py file', required=True)
    args = parser.parse_args()
    tree = ast.parse(open(args.input).read())
    calls = get_func_calls(tree)
    output(calls)


 