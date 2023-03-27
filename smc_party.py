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

        #TODO modify this for the first participant , check with TAs on how to  , take min ? 
        self.is_first_party = (min(self.protocol_spec.participant_ids) >= self.client_id)
        self.local_shares = self.share_secrets()



    def share_secrets(self) -> Dict[str,Share]:
        num_participants = len(self.protocol_spec.participant_ids)
        local_shares = {} 
        
        for key,value in self.value_dict.items():
            shares = share_secret(value, num_participants)

            shares_and_ids = zip(shares, self.protocol_spec.participant_ids)

            for share, id in shares_and_ids:
                if id == self.client_id:
                    local_shares[key.id] = share
                else:
                    self.comm.send_private_message(id, key.id, share.serialize())
        
        return local_shares





    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """

        expr = self.protocol_spec.expr

        # Evaluate Expression
        local_share = self.process_expression(expr)

        # Share evaluation with other parties
        #TODO Correct encoding
        label = expr.id.decode("utf-8")
        to_send = local_share.serialize()
        self.comm.publish_message(label,to_send)

        shares = [local_share]
        # Retrieve other shares
        for pid in [pid for pid in self.protocol_spec.participant_ids if pid != self.client_id]:
            label = expr.id.decode("utf-8") 
            pid_share = Share.deserialize(self.comm.retrieve_public_message(pid,label))
            shares.append(pid_share)

        return reconstruct_secret(shares)


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ):

        p = self.process_expression
        
        if isinstance(expr, AddOp):
            return p(expr.a) + p(expr.b)
        
        elif isinstance(expr,AddKOp):
            if self.is_first_party:
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
            if expr.id not in self.local_shares.keys():
                share = Share.deserialize(self.comm.retrieve_private_message(expr.id))
                self.local_shares[expr.id] = share
            return self.local_shares[expr.id]




    

    #TODO implement beaver : https://github.com/fumiyanll23/beaver-triplet/blob/main/BeaverTriplet.py
    # https://medium.com/applied-mpc/a-crash-course-on-mpc-part-2-fe6f847640ae
    def beaver(self,expr):
        pass
    

if __name__ == '__main__':
    exp = Scalar(4)*Scalar(6)+ Scalar(3)
    x = SMCParty('0','0',0,None,{})
    p = x.process_expression
    print(p(exp))
    print("Hello")

