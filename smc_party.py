"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import collections
import json
from expression import *
from typing import (
    Dict,
    Set,
    Tuple,
    Union
)

from communication import Communication
from expression import (
    Expression,
    Secret
)
from protocol import ProtocolSpec
from secret_sharing import(
    reconstruct_secret,
    share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
        ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict

        #TODO modify this for the first participant , check with TAs on how to 
        self.is_first_party = False


    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        raise NotImplementedError("You need to implement this method.")


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ):

        #Here we need to call the corresponding protocol to the operations , first we can treat scalars as secrets , then optimize
        #after we know that the implementation works
        p = self.process_expression
        
        if isinstance(expr, AddOp):
            return p(expr.a) + p(expr.b)
        
        elif isinstance(expr,AddKOp):
            if self.client_id == self.is_first_party:
                k = Share(expr.b.value)
            else:
                k = Share()
            return k + p(expr.a)
        
        elif isinstance(expr,SubOp):
            return p(expr.a)-p(expr.b)
        
        elif isinstance(expr,MultOp):
            return self.beaver(expr)
        
        elif isinstance(expr, MultKOp):
            return p(expr.a) * p(expr.b)
        
        elif isinstance(expr,Scalar):
            return Share(expr.value)
        
        elif isinstance(expr,Secret):
            #TODO What to do when its a secret , retrieve secret share 
            pass



    

    #TODO implement beaver : https://github.com/fumiyanll23/beaver-triplet/blob/main/BeaverTriplet.py
    # https://medium.com/applied-mpc/a-crash-course-on-mpc-part-2-fe6f847640ae
    def beaver(self,mult_expr):
        raise NotImplementedError("Not Implemented yet")

