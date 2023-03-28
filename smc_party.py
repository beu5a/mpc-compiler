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
        self.is_first_party = (min(self.protocol_spec.participant_ids) == self.client_id)
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
    

    def send_and_reconstruct_share(self, local_share, shr_id : str = None):
        """
        Method to send the local share of a value to the server and reconstruct the value from the other participant's shares.
        """
        
        # Evaluate Expression
        # Share evaluation with other parties
        label = shr_id
        to_send = local_share.serialize()
        self.comm.publish_message(label, to_send)

        shares = [local_share]
        # Retrieve other shares
        for pid in [pid for pid in self.protocol_spec.participant_ids if pid != self.client_id]:
            pid_share = Share.deserialize(self.comm.retrieve_public_message(pid,label))
            shares.append(pid_share)

        return reconstruct_secret(shares)



    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """

        expr = self.protocol_spec.expr
        local_share = self.process_expression(expr)
        return self.send_and_reconstruct_share(local_share,expr.id.decode("utf-8"))


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ):

        p = self.process_expression
        
        if isinstance(expr, AddOp):
            return p(expr.a) + p(expr.b)
        
        elif isinstance(expr,AddKOp):
            k2 = p(expr.a)
            if self.is_first_party:
                k = Share(expr.b.value)
            else:
                k = Share()
            if isinstance(expr.a, Scalar):
                if self.is_first_party:
                    k2 = Share(expr.a.value)
                else:
                    k2 = Share()
                
            return k + k2
        
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


    def beaver(self,mult_expr):
        """
        Function that implements the beaver triplet generation protocol
        """
        #first we get [a], [b], [c] from the trusted third party
        (a,b,c) = self.comm.retrieve_beaver_triplet_shares(mult_expr.id)

        #We need [x] and [y], mult_expr.a and mult_expr.b, but we need to process them in case they are not leaves
        x = self.process_expression(mult_expr.a)
        y = self.process_expression(mult_expr.b)



    #TODO: A voir avec Yassine comment recupérer d et e et envoyer [d] et [e] aux autres parties
                #Je pense que je devrai faire une fonction, mais peut etre que c'est dans le dictionnaire et run avec la classe
                #Après reflexion je suis 80% sure que c'est pas la même que dans run donc on peut mettre une fonction utilitaire
                #Confirmer avec Yassine.
        
        #We share [d] = [x-a] and retrieve d = (x-a) from the published shares
        d = Share(self.send_and_reconstruct_share(x-a, mult_expr.id.decode("utf-8") + "_d" ))
        #We share [e] = [y-b] and retrieve e = (y-b) from the other parties
        e = Share(self.send_and_reconstruct_share(y-b, mult_expr.id.decode("utf-8") + "_e"))
        
        #We compute [z] = [c] + [x]*e + [y]*d - (ed if first party, 0 otherwise)

        return c + x * e + y * d - (e * d if self.is_first_party else Share(0))
