# Secure Multi-party Computation System


In this project, we have developped a secure multi-party computation system in
Python 3.


### Files

Our implementation contains the following files.

* `expression.py`—Tools for defining arithmetic expressions.
* `secret_sharing.py`—Secret sharing scheme
* `ttp.py`—Trusted parameter generator for the Beaver multiplication scheme.
* `smc_party.py`—SMC party implementation
* `manif.py` — Class to define the arithmetic circuit used in our use case.
* `test_integration.py`—Integration test suite.
* `test_ttp.py`—Test suite for the trusted parameter generator.

Code that handles the communication. 
* `protocol.py`—Specification of SMC protocol
* `communication.py`—SMC party-side of communication
* `server.py`—Trusted server to exchange information between SMC parties

Code for our performance test.
* `performance.py` —Test suite for evaluating the performance of our protocol (added for information purposes but will not run without changed made to the rest of the code, for more information see report)

### Custom application
Our arithmetic circuit is implemented in `manif.py`, to see an example on how to use it, see the test called manif in `test_integration.py`

### How to run tests

The tests are implemented using *pytest*, to run them use the command
```
python3 -m pytest
```
in the directory of project.
