"""
Secret sharing scheme.
"""

from __future__ import annotations

from typing import List , Optional
from random import randint
import json

class Share:
    """
    A secret share in a finite field.
    """

    #this modulus provides 256 bits of security
    MODULUS = 101855371129257486166347889299578665493313847995829888078830076277971759798433


    def __init__(self, n :Optional[int] = 0):
        self._value = n % Share.MODULUS

    def __repr__(self):
        # Helps with debugging.
        return "Share({})".format(self._value)
    
    def __int__(self):
        return self._value
    
    def __len__(self):
        return len(str(self._value))

    def __add__(self, other):
        if isinstance(other,Share):
            return Share(self._value + other._value)
        elif isinstance(other,int):
            return Share(self._value + other)
        else :
            raise NotImplementedError
        
    def __radd__(self, other):
        return self.__add__(other)

    
    def __sub__(self, other):
        if isinstance(other,Share):
            return Share(self._value - other._value)
        elif isinstance(other,int):
            return Share(self._value - other)
        else :
            raise NotImplementedError
        
    def __rsub__(self, other):
        s = self.__sub__(other)
        return Share(- s._value)

    def __mul__(self, other):
        if isinstance(other,Share):
            return Share(self._value * other._value)
        elif isinstance(other,int):
            return Share(self._value * other)
        else :
            raise NotImplementedError
        
    def __rmul__(self, other):
        return self.__mul__(other)

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        return json.dumps({'value': self._value})
        

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        deserialized = json.loads(serialized)
        return Share(deserialized['value'])


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    
    shares = [Share()]

    for _ in range(num_shares-1):
        share_i = Share(randint(0, Share.MODULUS))
        shares.append(share_i)

    shares[0] = Share(secret) - sum(shares)
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    return sum(shares)._value




