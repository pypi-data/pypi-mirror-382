# snowdrop-adjudicators
This contains two public adjudicators for the Tangled game, one using the Schrodinger equation and one
using simulated annealing. The Schrodinger equation adjudicator matches the ground truth output of the
quantum annealer for all problem instances up to the largest sizes I've been able to test (all the
terminal states of all the X-Prize graphs except the Mutant C60 graph), whereas the simulated annealing
solver, while enormously faster, makes deterministic adjudication errors as described in the 
[X-Prize Phase 1 Submission document](https://fqodzpifyovgmqjlluin.supabase.co/storage/v1/object/public/pdfs/XPRIZE_Phase_I_Submission_Snowdrop.pdf).
The simulated annealing solver's parameters were chosen to give unbiased sampling of all classically degenerate 
ground states of the diagonal Ising model part of the Hamiltonian, which fails to accurately compute game scores
for some terminal states due to not taking into account order-by-disorder effects.

## Using these adjudicators
Both included adjudicators have parameters that you need to set. To see the minimum number and type of
these for both, look at `test_schrodinger.py` and `test_simulated_annealing.py` which show how to set these
parameters and how to use the adjudicators themselves. To see the full suite of settable parameters, look at the
`schrodinger.py` and `simulated_annealing.py` files.

## What will happen if I train an agent using these adjudicators?
If you use the Schrodinger adjudicator, your agent will be learning from the ground truth, but you will be limited
to very small graphs, and training could take forever. If you want to go this route, you should enumerate all possible
terminal states for your graph, use the Schrodinger adjudicator to adjudicate all of them, and store the results in 
a lookup table. You can then create a new lookup table adjudicator (see next section) which will then be very fast.

If you use the simulated annealing adjudicator, you will get very fast results, but they will be systematically
wrong for some fraction of the terminal states. The more frustration in the ground states of your instance, the more
potential there is for getting a wrong answer. If you train an agent using this adjudicator, it will learn from a
corrupted reward signal and may perform poorly.

## Building your own adjudicators
If you have an idea for how to spoof the quantum annealing hardware more effectively, for example using
tensor networks, you can build your own adjudicator. Just follow the pattern in `simulated_annealing.py`. 
Subclass the `Adjudicator` base class, define the adjudicator's parameters and a setup method, and then 
define your adjudication method. Ensure that the adjudicate method takes a `GameState` instance as input 
and returns an `AdjudicationResult` object as output. 

**Important Note:** If you want to enter an agent into the \$10,000 Mutant $C_{60}$ prize challenge, using output of the 
D-Wave quantum annealing hardware as part of an adjudicator is strictly forbidden.

## Running unit tests
There are two unit tests here, one per adjudicator. If you build a new adjudicator I strongly recommend following the
unit test pattern here and adding the exact same type of test for your new adjudicator.