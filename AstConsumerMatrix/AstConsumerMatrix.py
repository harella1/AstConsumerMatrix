'''
Get all function calls from a python file

The MIT License (MIT)
Copyright (c) 2016 Suhas S G <jargnar@gmail.com>
'''
import ast
from collections import deque
from collections import namedtuple
Module = namedtuple("Module",["Structors","Functionals","Provider","Consumer"])
d = {}

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
            if node.value.id != 'self':
                self._name.appendleft(node.attr)
                self._name.appendleft(node.value.id)
        except AttributeError:
            self.generic_visit(node)

imports = set()
def get_func_calls(module_name,tree):
    for node in ast.walk(tree):
       if isinstance(node, ast.ClassDef):
            d[module_name].Structors.add(node.name)
            for n in ast.walk(node):
                if isinstance(n, ast.FunctionDef):
                    d[module_name].Functionals.add(n.name)
                    d[module_name].Provider.add((node.name,n.name))                

            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    callvisitor = FuncCallVisitor()
                    callvisitor.visit(n.func)
                    d[module_name].Consumer.add((node.name,callvisitor.name))
       if isinstance(node, ast.FunctionDef) and node.name not in d[module_name].Functionals:
          d[module_name].Structors.add(module_name)
          d[module_name].Functionals.add(node.name)
          d[module_name].Provider.add((module_name,node.name))                
          for n in ast.walk(node):
             if isinstance(n, ast.Call):
                callvisitor = FuncCallVisitor()
                callvisitor.visit(n.func)
                d[module_name].Consumer.add((node.name,callvisitor.name))


    while len(imports) > 0:
        try:
            modulename = imports.pop()
            mod = __import__(modulename)
            if hasattr(mod, '__file__') and mod.__file__.endswith('.py'):
                tree1 = ast.parse(open(mod.__file__, encoding='utf8').read())
                get_func_calls(module_name,tree1)
            else:
                continue
        except Exception as ex:
            print ("Unexpected error:", ex.msg)
            pass

    return d


def output(d):
    import numpy as np
    from matplotlib import pyplot as plt
    from matplotlib import gridspec as mtgs
    from matplotlib.backends.backend_pdf import PdfPages

    for mod in d:    
        if len(d[mod].Provider) == 0:
            continue
        x = list(d[mod].Structors)
        y = list(d[mod].Functionals)
        Interfaces = np.zeros((len(y),len(x)), dtype=np.int)
        Dependencies = np.zeros((len(y),len(x)), dtype=np.int)
        for item,method in d[mod].Provider:
            Interfaces[y.index(method),x.index(item)] = 1
        for method,item in list(set(d[mod].Consumer)):
            if method in y and item in x:
                Dependencies[y.index(method),x.index(item)] = 1

        fig = plt.figure(figsize = (len(x),len(y)))
        fig.suptitle(mod, fontsize=18)           
        gs = mtgs.GridSpec(nrows=2,ncols=1,right=0.98)

        vals = Interfaces*-100+300

        ax1 = fig.add_subplot(gs[0])
        ax1.axis('off')
        ax1.set_title('Provider')
        the_table = ax1.table(cellText=Interfaces, loc='center',cellLoc='center',rowLabels=y, colLabels=x,cellColours=plt.cm.hot(vals))
        #[the_table._cells[(i,0)].set_width(0.1) for i in range(0,len(y))]

        vals = Dependencies*-100+300
        ax2 = fig.add_subplot(gs[1])
        ax2.axis('off')
        ax2.set_title('Consumer')
        the_table = ax2.table(cellText=Dependencies, loc='center',cellLoc='center',rowLabels=y, colLabels=x,cellColours=plt.cm.hot(vals))
        #the_table.scale(1.5, 1.5)
        #fig.subplots_adjust(left=0.3),colWidths=[0.15]*len(y),colWidths=[0.15]*len(y)
        #plt.show()
        plt.savefig(mod+'.pdf',bbox_inches='tight')
        plt.close('all')

    

if __name__ == '__main__':
    import os
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input .py file', required=True)
    args = parser.parse_args()
    module_dir = os.path.dirname(os.path.dirname(args.input))
    sys.path.append(module_dir)
    tree = ast.parse(open(args.input).read())
    for node in ast.walk(tree):
       if isinstance(node, ast.Import) and node.names[0].name not in d:
            imports.add(node.names[0].name)
       if isinstance(node, ast.ImportFrom) and node.module not in d:
            imports.add(node.module)

    module_name = os.path.splitext(os.path.basename(args.input))[0]
    d[module_name] = Module(set(),set(),set(),set())
    
    calls = get_func_calls(module_name,tree)
    output(calls)

