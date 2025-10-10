import math
from collections import defaultdict
from typing import Generic

from flippy.core import ProgramState, ReturnState, SampleState, ObserveState, InitialState
from flippy.interpreter import CPSInterpreter
from flippy.distributions import Categorical, RandomNumberGenerator
from flippy.types import Element
from flippy.inference.inference import InferenceAlgorithm, DiscreteInferenceResult

class SamplePrior(InferenceAlgorithm[Element]):
    """Sample from the prior and ignore observation statements"""
    def __init__(self, function, samples : int, seed=None):
        self.function = function
        self.seed = seed
        self.samples = samples

    @property
    def is_cachable(self):
        return self.seed is not None

    def run(self, *args, **kws) -> Categorical[Element]:
        rng = RandomNumberGenerator(self.seed)
        return_counts = defaultdict(int)
        init_ps = CPSInterpreter().initial_program_state(self.function)
        for _ in range(self.samples):
            ps = init_ps.step(*args, **kws)
            while not isinstance(ps, ReturnState):
                if isinstance(ps, SampleState):
                    value = ps.distribution.sample(rng=rng)
                    ps = ps.step(value)
                elif isinstance(ps, ObserveState):
                    ps = ps.step()
                else:
                    raise ValueError("Unrecognized program state message")
            return_counts[ps.value] += 1
        total_prob = sum(return_counts.values())
        return_probs = {e: p/total_prob for e, p in return_counts.items()}
        marginal_likelihood = total_prob / self.samples
        return DiscreteInferenceResult(
            support=list(return_probs.keys()),
            probabilities=list(return_probs.values()),
            marginal_likelihood=marginal_likelihood
        )
