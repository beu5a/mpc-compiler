from random import randint
from server import run
from expression import Expression, Scalar, Secret
from typing import (
    Dict,
    Set,
    Tuple,
    Union
)
from protocol import ProtocolSpec
from smc_party import SMCParty


class Manif:
        """
        A Group of people linked to a demonstration

    Attributes:
        participants: Dictionary containing the participants of the demonstration, with their respective secrets (The fine they had to pay, the amount they want to give and 1 if they were fined or not)
        sponsors: Dictionary conataining the sponsors of the demonstration, with the amount the are willing to pay per fined activist
    """
        def __init__(
            self,
            participants: Dict[str, Dict[Secret, int]],
            sponsors: Dict[str, Dict[Secret, int]],
            ):

            self.participants = participants
            self.sponsors = sponsors


        # We use an expression to define the arithmetic circuit need to compute the total amount that will need to be paid

        # expr_fine = sum(x_i) which is the sum of all the fines
        #expr_fined (=p) is the number of fined participants
            self.expr_fine = Scalar(0)
            self.expr_fined = Scalar(0)
            self.expr_buffer = Scalar(0)
    
            for participant in participants.values():
                self.expr_fine += list(participant.keys())[0]
                self.expr_fined += list(participant.keys())[2]
                self.expr_buffer += list(participant.keys())[1]

        
        # expr_sponsor = sum(y_i*p) which is the sum of all the sponsorships
            self.expr_sponsor = Scalar()
            for sponsor in sponsors.values():
                self.expr_sponsor +=  list(sponsor.keys())[0]
            self.expr_sponsor *= self.expr_fined

        #The expected amount to pay = sum(x_i) - sum(y_i*p) - sum(y_i)

            self.expr_to_pay = self.expr_fine - self.expr_sponsor - self.expr_buffer

            self.parties = participants.copy()
            self.parties.update(sponsors)

