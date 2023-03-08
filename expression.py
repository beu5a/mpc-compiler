"""
Tools for building arithmetic expressions to execute with SMC.

Example expression:
>>> alice_secret = Secret()
>>> bob_secret = Secret()
>>> expr = alice_secret * bob_secret * Scalar(2)

MODIFY THIS FILE.
"""

import base64
import random
from typing import Optional


ID_BYTES = 4


def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)


class Expression:
    """
    Base class for an arithmetic expression.
    """

    def __init__(
            self,
            id: Optional[bytes] = None
        ):
        # If ID is not given, then generate one.
        if id is None:
            id = gen_id()
        self.id = id

    def __add__(self, other):
        return AddOp ( self , other )


    def __sub__(self, other):
        raise NotImplementedError("You need to implement this method.")
        #should we use scalar (-1) or create a new class for this


    def __mul__(self, other):
        return MultOp ( self , other )


    def __hash__(self):
        return hash(self.id)


    # Feel free to add as many methods as you like.


    #TODO :to be removed 
    def traverse(expr):
        if isinstance(expr,AddOp):
            return Expression . traverse(expr.a) + Expression . traverse(expr.b) 
        if isinstance(expr,MultOp):
            return  Expression . traverse(expr.a) * Expression . traverse(expr.b)
        if isinstance(expr,Scalar):
            return expr
        if isinstance(expr,Secret):
            return expr


    
class AddOp ( Expression ) :
    def __init__ ( self , a , b ) :
        self . a = a
        self . b = b



# Intermediate tree node representing multipl ication operation .
# ( Note it is now an instance of Expression )
class MultOp ( Expression ) :
    def __init__ ( self , a , b ) :
        self . a = a
        self . b = b


# Leaf node representing a variable .
# ( Note it is now an instance of Expression ) 
#Here only for reference implementation , ie equivalent to scalar
class Variable ( Expression ) :
    def __init__ ( self , name = None ) :
        self . name = name




class Scalar(Expression):
    """Term representing a scalar finite field value."""

    def __init__(
            self,
            value: int,
            id: Optional[bytes] = None
        ):
        self.value = value
        super().__init__(id)


    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"


    def __hash__(self):
        return


    # Feel free to add as many methods as you like.





class Secret(Expression):
    """Term representing a secret finite field value (variable)."""
    """leaf,  """



    def __init__(
            self,
            id: Optional[bytes] = None,
            value: Optional[int] = None
        ):
        super().__init__(id)
        self.value  = value


    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.value if self.value is not None else ''})"
        )


    # Feel free to add as many methods as you like.


# Feel free to add as many classes as you like.
