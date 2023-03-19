"""
Trusted parameters generator.
"""

import collections
from typing import (
    Dict,
    Set,
    Tuple,
)

from communication import Communication
from secret_sharing import(
    share_secret,
    Share,
)
from random import randint


#For this implementation to work we need all participants to be added before the shares are retrieved.

class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        self.shares: Dict[(str, str), Tuple[Share, Share, Share]] = {}
        self.op_ids: Set[str] = set()


    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """
        if client_id not in self.participant_ids :
            raise ValueError("Client ID not valid")
        if op_id not in self.op_ids: 
            self.gen_beaver_triplet(op_id)
            self.op_ids.add(self, op_id)
        return self.shares[(client_id,op_id)]
        
    def gen_beaver_triplet(self, op_id: str) -> None:
        """
        Generate a beaver triplet and it's secret shares for each participant.
        """
        a = randint(0, Share.MODULUS )
        b = randint(0, Share.MODULUS )
        c = (a * b) % Share.MODULUS
        
        num_shares = len(self.participant_ids)
        
        shares_a = share_secret(a, num_shares)
        shares_b = share_secret(b, num_shares)
        shares_c = share_secret(c, num_shares)

        
        for i, client_id in enumerate(self.participant_ids):
            self.shares[(op_id, client_id)] = (shares_a[i], shares_b[i], shares_c[i])

    
