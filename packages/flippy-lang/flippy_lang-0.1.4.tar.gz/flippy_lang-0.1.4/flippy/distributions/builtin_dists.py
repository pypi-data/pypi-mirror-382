import sys
from typing import Tuple, Sequence, Union, Any, Callable, Generic, TypeVar
from dataclasses import is_dataclass, asdict
from itertools import combinations_with_replacement
from collections import Counter, defaultdict
import math

from flippy.tools import isclose, ISCLOSE_ATOL, ISCLOSE_RTOL, PackagePlaceholder
from functools import cached_property
from flippy.distributions.base import Distribution, FiniteDistribution, Element
from flippy.distributions.support import \
    Interval, Range, Simplex, OrderedIntegerPartitions, UnionSet
from flippy.distributions.random import default_rng

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = PackagePlaceholder("matplotlib.pyplot")

try:
    import numpy as np
except ImportError:
    np = PackagePlaceholder("numpy")

def beta_function(*alphas):
    num = math.prod(math.gamma(a) if not isclose(a, 0) else float('inf') for a in alphas)
    den = math.gamma(sum(alphas))
    return num/den


class Bernoulli(FiniteDistribution):
    '''
    A Bernoulli distribution. The support is a boolean value, with a single
    parameter `p` that specifies the probability of the value `True`.
    '''
    support = (True, False)
    def __init__(self, p=.5):
        self.p = p
    def sample(self, rng=default_rng, name=None, initial_value=None) -> bool:
        if rng.random() <= self.p:
            return True
        return False
    def log_probability(self, element):
        return {
            True: math.log(self.p) if self.p != 0.0 else float('-inf'),
            False: math.log(1 - self.p) if self.p != 1.0 else float('-inf')
        }.get(element, float('-inf'))
    def __repr__(self):
        return f"Bernoulli(p={self.p})"


MarginalElement = TypeVar('MarginalElement')

def is_namedtuple(obj):
    return (
        isinstance(obj, tuple) and
        hasattr(obj, '_asdict') and
        hasattr(obj, '_fields')
    )

class Categorical(FiniteDistribution[Element]):
    '''
    A distribution over a discrete support. Defaults to uniform probability of
    each item, unless `probabilities` or `weights` are specified.

    - `support` lists the discrete support.
    - `probabilities` is optional. Specifies the probabilities of each item of
    the support.
    - `weights` is optional. Specifies the weight for each item of the support.
    Transformed to probabilities by normalizing by the sum of weights.
    '''
    def __init__(self, support, *, probabilities=None, weights=None):
        if probabilities is not None:
            assert isclose(sum(probabilities), 1, atol=ISCLOSE_ATOL, rtol=ISCLOSE_RTOL)
        elif weights is not None:
            total_weight = sum(weights)
            probabilities = [w / total_weight for w in weights]
            del weights
        else:
            probabilities = [1/len(support) for _ in support]
        assert len(probabilities) == len(support), f'Expected the size of support ({len(support)}) to match the length of weights/probabilities ({len(probabilities)}), but they do not.'
        self.support = support
        self._probabilities = probabilities

    @classmethod
    def from_dict(cls, d: dict[Element, float]):
        support, probs = zip(*d.items())
        return cls(support=support, probabilities=probs)

    @classmethod
    def from_continuous(cls, dist: Distribution[Element], support: Sequence[float]):
        probs = [dist.prob(s) for s in support]
        total = sum(probs)
        probs = [p/total for p in probs]
        return cls(support=support, probabilities=probs)

    @property
    def probabilities(self):
        return self._probabilities

    def sample(self, rng=default_rng, name=None, initial_value=None) -> Element:
        return rng.choices(self.support, weights=self._probabilities, k=1)[0]

    def log_probability(self, element) -> float:
        try:
            return math.log(self._probabilities[self.support.index(element)])
        except ValueError:
            return float('-inf')

    def __repr__(self):
        return f"{self.__class__.__name__}(support={self.support}, probabilities={self._probabilities})"

    def _default_repr_html_(self):
        format_prob = lambda p: f"{p:.3f}" if p > 0.001 else f"{p:.2e}"
        try:
            support = sorted(self.support)
        except TypeError:
            support = sorted(self.support, key=lambda s: -self.prob(s))
        return ''.join([
            "<table>",
            "<thead><tr><th>Element</th><th>Probability</th></tr></thead>",
            "<tbody>",
            *(
                [
                    f"<tr><td>{s}</td><td>{format_prob(self.prob(s))}</td></tr>"
                    for i, s in enumerate(support)
                ] if len(support) < 10 else (
                    [
                        f"<tr><td>{s}</td><td>{format_prob(self.prob(s))}</td></tr>"
                        for i, s in enumerate(support[:5])
                    ] + [
                        "<tr><td>...</td><td>...</td><td>...</td></tr>"
                    ] + [
                        f"<tr><td>{s}</td><td>{format_prob(self.prob(s))}</td></tr>"
                        for i, s in zip(range(len(support), len(support) - 5, -1), support[-5:])
                    ]
                )
            ),
            "</tbody>",
            "</table>"
        ])

    def _ReturnDict_repr_html(self):
        format_prob = lambda p: f"{p:.3f}" if p > 0.001 else f"{p:.2e}"
        keys = set()
        support = []
        probs = []
        try:
            sorted_support = sorted(self.support)
        except TypeError:
            sorted_support = sorted(self.support, key=lambda s: -self.prob(s))
        for e in sorted_support:
            prob = self.prob(e)
            probs.append(prob)
            if is_dataclass(e):
                e = asdict(e)
            elif is_namedtuple(e):
                e = e._asdict()
            assert isinstance(e, dict)
            support.append(e)

        for e in support:
            keys.update(e.keys())
        def make_row(e : dict, p : float):
            row = []
            for k in keys:
                row.append(f"<td>{str(e.get(k, ''))}</td>")
            row.append(f"<td>{format_prob(p)}</td>")
            return f"<tr>{''.join(row)}</tr>"

        rows = []
        if len(support) < 10:
            for e, p in zip(support, probs):
                rows.append(make_row(e, p))
        else:
            for e, p in zip(support[:5], probs[:5]):
                rows.append(make_row(e, p))
            rows.append("<tr><td>...</td></tr>")
            for e, p in zip(support[-5:], probs[-5:]):
                rows.append(make_row(e, p))

        return ''.join([
            "<table>",
            "<thead><tr>"+''.join([f"<th>{k}</th>" for k in keys])+"<th>Probability</th></tr></thead>",
            "<tbody>",
            *rows,
            "</tbody>",
            "</table>"
        ])

    def _repr_html_(self):
        if (
            all(isinstance(e, dict) for e in self.support) or \
            all(is_dataclass(e) for e in self.support) or \
            all(is_namedtuple(e) for e in self.support)
        ):
            return self._ReturnDict_repr_html()
        return self._default_repr_html_()

    def plot(self, ax=None, bins=100, **kwargs):
        element = next(iter(self.support))
        if isinstance(element, (int, float)):
            return self._plot_1d(ax=ax, bins=bins, **kwargs)
        elif isinstance(element, (list, tuple)) and len(element) == 2:
            return self._plot_2d(ax=ax, bins=bins, **kwargs)
        elif isinstance(element, dict):
            if len(element) == 1:
                key = next(iter(element.keys()))
                dist = self.marginalize(lambda d : d[key])
                ax = dist._plot_1d(ax=ax, bins=bins, **kwargs)
                ax.set_xlabel(key)
                return ax
            if len(element) == 2:
                xkey, ykey = list(element.keys())
                dist = self.marginalize(lambda d : (d[xkey], d[ykey]))
                ax = dist._plot_2d(ax=ax, bins=bins, **kwargs)
                ax.set_xlabel(ykey)
                ax.set_ylabel(xkey)
                return ax
        elif is_dataclass(element):
            if len(element.__annotations__) == 1:
                key = next(iter(element.__annotations__))
                dist = self.marginalize(lambda d : getattr(d, key))
                ax = dist._plot_1d(ax=ax, bins=bins, **kwargs)
                ax.set_xlabel(key)
                return ax
            if len(element.__annotations__) == 2:
                xkey, ykey = element.__annotations__
                dist = self.marginalize(lambda d : (getattr(d, xkey), getattr(d, ykey)))
                ax = dist._plot_2d(ax=ax, bins=bins, **kwargs)
                ax.set_xlabel(ykey)
                ax.set_ylabel(xkey)
                return ax
        raise NotImplementedError("Can't plot this distribution")

    def _plot_2d(self, ax=None, bins=100, **kwargs):
        assert all(isinstance(s, (list, tuple)) and len(s) == 2 for s in self.support)
        if ax is None:
            fig, ax = plt.subplots()
        kwargs = {
            **{'origin': 'lower', 'aspect': 'auto'},
            **kwargs
        }
        xs, ys = zip(*self.support)
        hist, xedges, yedges = np.histogram2d(x=xs, y=ys, bins=bins, weights=self.probabilities)
        xlen = xedges[-1] - xedges[0]
        xmid = xlen/2
        xedges = [xmid - (xlen/2)*1.05, xmid + (xlen/2)*1.05]
        ymid = (yedges[0] + yedges[-1])/2
        ylen = yedges[-1] - yedges[0]
        yedges = [ymid - (ylen/2)*1.05, ymid + (ylen/2)*1.05]
        extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
        ax.imshow(hist, extent=extent, **kwargs)
        cbar = ax.figure.colorbar(ax.images[0], ax=ax, location='right')
        cbar.set_label('Probability')
        return ax

    def _plot_1d(self, ax=None, bins=100, **kwargs):
        assert all(isinstance(s, (int, float)) for s in self.support)
        if ax is None:
            fig, ax = plt.subplots()
        ax.hist(self.support, weights=self.probabilities, bins=bins, **kwargs)
        ax.set_ylabel("Probability")
        return ax

    def marginalize(self, projection: Callable[[Element], MarginalElement]) -> 'Categorical[MarginalElement]':
        d = defaultdict(float)
        for s, p in zip(self.support, self.probabilities):
            d[projection(s)] += p
        return Categorical.from_dict(d)

    def condition(self, likelihood: Callable[[Element], float]) -> 'Categorical[Element]':
        posterior = {}
        for e, prior in self.items():
            l = likelihood(e)
            if l == 0:
                continue
            posterior[e] = prior * l
        norm = sum(posterior.values())
        return Categorical.from_dict({e: p/norm for e, p in posterior.items()})


class Multinomial(FiniteDistribution):
    '''
    This distribution takes multiple samples from a `Categorical` distribution.
    It takes the same parameters as `Categorical`, with the addition of `trials`,
    which are the number of samples drawn from the `Categorical`.
    '''
    def __init__(self, categorical_support, trials, *, probabilities=None, weights=None):
        self.categorical = Categorical(
            categorical_support,
            probabilities=probabilities,
            weights=weights
        )
        self.trials = trials

    def sample(self, rng=default_rng, name=None, initial_value=None) -> Tuple[int, ...]:
        samples = rng.choices(
            self.categorical.support,
            weights=self.categorical._probabilities,
            k=self.trials
        )
        counts = Counter(samples)
        return tuple(counts.get(i, 0) for i in self.categorical.support)

    @cached_property
    def support(self):
        return OrderedIntegerPartitions(
            total=self.trials, partitions=len(self.categorical.support)
        )

    def log_probability(self, vec):
        if vec in self.support:
            probs = self.categorical._probabilities
            num1 = math.gamma(self.trials + 1)
            num2 = math.prod(p**x for p, x in zip(probs, vec))
            den = math.prod(math.gamma(x + 1) for x in vec)
            return math.log((num1*num2)/den)
        return float('-inf')


class Gaussian(Distribution):
    r'''
    A Gaussian distribution, with support over the real numbers $\mathbb{R}$.

    - `mean` is the mean.
    - `sd` is the standard deviation.
    '''

    support = Interval(float('-inf'), float('inf'), left_open=True, right_open=True)
    def __init__(self, mean=0, sd=1):
        self.mean = mean
        self.sd = sd

    def sample(self, rng=default_rng, name=None, initial_value=None) -> float:
        return rng.gauss(self.mean, self.sd)

    def log_probability(self, element):
        prob = (
            math.e**(-.5*((element - self.mean)/self.sd)**2)
        )/(
            self.sd*(2*math.pi)**.5
        )
        return math.log(prob) if prob > 0. else float('-inf')
Normal = Gaussian


class Uniform(Distribution):
    '''
    A Uniform distribution, with support over a specified interval [`start`, `end`].

    - `start` defaults to 0. The lower bound of the interval.
    - `end` defaults to 1. The upper bound of the interval.
    '''

    def __init__(self, start=0, end=1):
        self.start = start
        self.end = end
        self.support = Interval(start, end, left_open=False, right_open=False)

    def sample(self, rng=default_rng, name=None, initial_value=None) -> float:
        return rng.uniform(self.start, self.end)

    def log_probability(self, element):
        if element in self.support:
            return math.log(1/(self.end - self.start))
        return float('-inf')


class Beta(Distribution):
    """
    A Beta distribution, with support over the interval [0, 1].
    - `alpha` is the first shape parameter (default 1).
    - `beta` is the second shape parameter (default 1).
    """
    support = Interval(0, 1, left_open=False, right_open=False)
    def __init__(self, alpha=1, beta=1):
        self.a = alpha
        self.b = beta

    def sample(self, rng=default_rng, name=None, initial_value=None) -> float:
        return rng.betavariate(self.a, self.b)

    def log_probability(self, element):
        if element in self.support:
            # to avoid numerical issues at the boundaries
            element = max(min(element, 1 - sys.float_info.epsilon), sys.float_info.epsilon)
            num = (element**(self.a - 1))*(1 - element)**(self.b - 1)
            prob = num/beta_function(self.a, self.b)
            return math.log(prob) if prob != 0 else float('-inf')
        return float('-inf')

    def plot(self, ax=None, bins=100, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        x = np.linspace(0, 1, 1000)
        ax.plot(x, [self.prob(i) for i in x], **kwargs)
        return ax


class Binomial(Distribution):
    """
    A Binomial distribution, with support over the integers [0, trials].

    - `trials` is the number of trials
    - `p` is the probability of success on each trial
    """

    def __init__(self, trials : int, p : float):
        self.trials = trials
        self.p = p
        assert 0 <= p <= 1
        self.support = tuple(range(0, self.trials + 1))

    def sample(self, rng=default_rng, name=None, initial_value=None) -> int:
        return sum(rng.random() < self.p for _ in range(self.trials))

    def log_probability(self, element):
        if element in self.support:
            prob = (
                math.comb(self.trials, element)
            )*(
                self.p**element
            )*(
                (1 - self.p)**(self.trials - element)
            )
            return math.log(prob) if prob != 0 else float('-inf')
        return float('-inf')


class Geometric(Distribution):
    """
    A Geometric distribution, with support over the non-negative integers {0, 1, 2, ...}.
    - `p` is the probability of success on each trial
    """

    support = Range(0, float('inf'))
    def __init__(self, p : float):
        self.p = p
        assert 0 <= p <= 1

    def sample(self, rng=default_rng, name=None, initial_value=None) -> int:
        i = 0
        while rng.random() >= self.p:
            i += 1
        return i

    def log_probability(self, element):
        if element in self.support:
            return math.log(
                ((1 - self.p)**(element))*self.p
            )
        return float('-inf')


class Poisson(Distribution):
    """
    A Poisson distribution, with support over the non-negative integers {0, 1, 2, ...}.
    """

    support = Range(0, float('inf'))
    def __init__(self, rate : float):
        self.rate = rate
        assert rate >= 0

    def sample(self, rng=default_rng, name=None, initial_value=None) -> int:
        p, k, L = 1, 0, math.exp(-self.rate)
        while p > L:
            k += 1
            p = rng.random()*p
        return k - 1

    def log_probability(self, k):
        if k not in self.support:
            return float('-inf')
        prob = (self.rate**k)*math.exp(-self.rate)/math.factorial(k)
        return math.log(prob)

class Gamma(Distribution):
    """
    A Gamma distribution, with support over the positive real numbers (0, inf).
    """

    support = Interval(0, float('inf'), left_open=False, right_open=True)
    def __init__(self, shape, rate):
        self.shape = shape
        self.rate = rate

    def sample(self, rng=default_rng, name=None, initial_value=None) -> float:
        # uses the shape, scale parameterization
        return rng.gammavariate(self.shape, 1/self.rate)

    def log_probability(self, element):
        if element in self.support:
            prob = (
                (self.rate**self.shape)*\
                (element**(self.shape - 1))*\
                math.exp(-self.rate*element)
            )/(
                math.gamma(self.shape)
            )
            return math.log(prob) if prob != 0 else float('-inf')
        return float('-inf')

class BetaBinomial(FiniteDistribution):
    """
    A Beta-Binomial compound distribution, with support over the integers [0, trials].
    """

    def __init__(self, trials : int, alpha=1, beta=1):
        self.alpha = alpha
        self.beta = beta
        self.trials = trials
        self.support = tuple(range(0, self.trials + 1))

    def sample(self, rng=default_rng, name=None, initial_value=None) -> int:
        p = rng.betavariate(self.alpha, self.beta)
        return sum(rng.random() < p for _ in range(self.trials))

    def log_probability(self, element):
        if element in self.support:
            prob = math.comb(self.trials, element)*(
                (
                    beta_function(element+self.alpha, self.trials - element + self.beta)
                )/(
                    beta_function(self.alpha, self.beta)
                )
            )
            return math.log(prob)
        return float('-inf')

    def update(self, data: Sequence[int]) -> 'BetaBinomial':
        assert all(0 <= d <= self.trials for d in data)
        new_alpha = self.alpha + sum(data)
        new_beta = self.beta + self.trials*len(data) - sum(data)
        return BetaBinomial(trials=self.trials, alpha=new_alpha, beta=new_beta)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(trials={self.trials}, alpha={self.alpha}, beta={self.beta})"


class Dirichlet(Distribution):
    """
    A Dirichlet distribution, with support over the (k-1)-simplex.
    - `alphas` is a sequence of shape parameters, one for each dimension of the simplex.
    """

    def __init__(self, alphas):
        self.alphas = alphas

    @cached_property
    def support(self):
        return Simplex(len(self.alphas))

    def sample(self, rng=default_rng, name=None, initial_value=None) -> Tuple[float, ...]:
        e = [rng.gammavariate(a, 1) for a in self.alphas]
        e = [ei if ei > 0 else sys.float_info.min for ei in e] # for numerical stability
        tot = sum(e)
        vals = tuple(ei/tot for ei in e)
        if 1 in vals:
            return tuple(min(ei, 1.0 - sys.float_info.epsilon) for ei in vals)
        return vals

    def log_probability(self, vec):
        r"""
        Log probability of a vector in the Dirichlet distribution:
        $$
        \ln P(x) = \sum_{i=1}^{k} (a_i - 1) \ln x_i - \ln B(a_1, a_2, \ldots, a_k)
        $$
        """
        if vec in self.support:
            log_num = sum((a - 1) * math.log(v) for v, a in zip(vec, self.alphas))
            log_den = math.log(beta_function(*self.alphas))
            return log_num - log_den
        return float('-inf')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(alphas={self.alphas})'


class DirichletMultinomial(FiniteDistribution):
    """
    A Dirichlet-Multinomial compound distribution, with support over the
    integer partitions of `trials` into `len(alphas)` parts.
    - `trials` is the number of trials
    - `alphas` is a sequence of shape parameters, one for each category.
    """

    def __init__(self, trials : int, alphas : Sequence[float]):
        self.alphas = alphas
        self.trials = trials

    @cached_property
    def support(self) -> OrderedIntegerPartitions:
        return OrderedIntegerPartitions(
            total=self.trials, partitions=len(self.alphas)
        )

    @cached_property
    def dirichlet(self) -> Dirichlet:
        return Dirichlet(self.alphas)

    def sample(self, rng=default_rng, name=None, initial_value=None) -> Tuple[int, ...]:
        ps = self.dirichlet.sample(rng=rng)
        samples = rng.choices(range(len(self.alphas)), weights=ps, k=self.trials)
        counts = Counter(samples)
        return tuple(counts.get(i, 0) for i in range(len(self.alphas)))

    def log_probability(self, vec : Tuple[int, ...]) -> float:
        if vec not in self.support:
            return float('-inf')
        assert len(vec) == len(self.alphas)
        num = self.trials*beta_function(sum(self.alphas), self.trials)
        den = math.prod(
            x*beta_function(a, x) for a, x in zip(self.alphas, vec)
            if x > 0
        )
        return math.log(num/den)

    def update(self, data : Sequence[Tuple[int, ...]]) -> 'DirichletMultinomial':
        assert all(len(d) == len(self.alphas) for d in data)
        assert all(sum(d) == self.trials for d in data)
        cat_counts = zip(*data)
        new_alphas = tuple(a + sum(c) for a, c in zip(self.alphas, cat_counts))
        return DirichletMultinomial(trials=self.trials, alphas=new_alphas)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(trials={self.trials}, alphas={self.alphas})"

class Mixture(Distribution):
    """
    A mixture distribution, which is a weighted combination of multiple distributions.
    - `distributions` is a sequence of `Distribution` instances to mix.
    - `weights` is an optional sequence of weights for each distribution. If not provided,
      uniform weights are assumed. Weights must sum to 1.

    - Alternatively, use the class method `from_distribution_of_distributions`
    to create a mixture from a `FiniteDistribution` over distributions.
    """

    def __init__(
        self,
        distributions : Sequence[Distribution],
        weights : Sequence[float] = None
    ):
        if weights is None:
            weights = [1 / len(distributions) for _ in distributions]
        assert len(distributions) == len(weights), "Must have a weight for each distribution"
        assert isclose(sum(weights), 1), "Weights must sum to 1"
        self.distributions = distributions
        self.weights = weights

    @classmethod
    def from_distribution_of_distributions(
        cls,
        dist_of_dists : FiniteDistribution[Distribution]
    ):
        probabilities = [dist_of_dists.prob(d) for d in dist_of_dists.support]
        return cls(
            distributions=dist_of_dists.support,
            weights=probabilities
        )

    @cached_property
    def support(self):
        return UnionSet(*(d.support for d in self.distributions))

    def sample(self, rng=default_rng, name=None, initial_value=None) -> Element:
        dist = rng.choices(self.distributions, weights=self.weights)[0]
        return dist.sample(rng=rng, name=name)

    def log_probability(self, element : Element) -> float:
        total_prob = 0
        for dist, weight in zip(self.distributions, self.weights):
            total_prob += weight * dist.prob(element)
        if total_prob == 0:
            return float('-inf')
        return math.log(total_prob)

    def expected_value(self, func: Callable[[Element], float] = lambda v : v) -> float:
        total_expected_value = 0
        for dist, weight in zip(self.distributions, self.weights):
            total_expected_value += weight * dist.expected_value(func=func)
        return total_expected_value

    def plot(self, *, ax=None, xmin=None, xmax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        if xmin is None:
            xmin = min([d.support.start for d in self.distributions])
        if xmax is None:
            xmax = max([d.support.end for d in self.distributions])
        x = np.linspace(xmin, xmax, 1000)
        ax.plot(x, [self.prob(i) for i in x], **kwargs)
        return ax
