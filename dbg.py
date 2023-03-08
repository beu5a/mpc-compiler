import base64
import random
from typing import Optional
from expression import *


##this was added by me for debugging purposes 

def print_ast(expr, indent=0):
    """
    Print an abstract syntax tree (AST) recursively.
    """
    if isinstance(expr, AddOp):
        print(' ' * indent + 'AddOp')
        print_ast(expr.a, indent+2)
        print_ast(expr.b, indent+2)
    elif isinstance(expr, MultOp):
        print(' ' * indent + 'MultOp')
        print_ast(expr.a, indent+2)
        print_ast(expr.b, indent+2)
    elif isinstance(expr, Scalar):
        print(' ' * indent + 'Scalar({})'.format(expr.value))
    elif isinstance(expr, Secret):
        print(' ' * indent + 'Secret({})'.format(expr.value))





if __name__ == '__main__':
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)


    x =  a + b  * c + Scalar(5)
    
    print_ast(x)




