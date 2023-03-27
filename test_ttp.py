"""
Unit tests for the trusted parameter generator.
Testing ttp is not obligatory.
"""

from ttp import TrustedParamGenerator


def test():
    ttp = TrustedParamGenerator()
    ttp.add_participant('Elisa')
    ttp.add_participant('Yassine')
    ttp.add_participant('Alice')
    ttp.add_participant('Bob')
    
    a = ttp.retrieve_share('Elisa', 'op1')
    b = ttp.retrieve_share('Yassine', 'op1')
    c = ttp.retrieve_share('Alice', 'op1')
    d = ttp.retrieve_share('Bob', 'op1')

    shares = [a,b,c,d]

    #Do I need to setup?




    
