import inspect
import os
import pkgutil
import random
from operator import itemgetter
from typing import List, Tuple, TypeVar

import numpy as np
import pandas as pd
import pytest
import rdflib

import pyrdf2vec
from pyrdf2vec.graphs import RDFLoader
from pyrdf2vec.samplers import Sampler
from pyrdf2vec.walkers import RandomWalker

np.random.seed(42)
random.seed(42)

LABEL_PREDICATE = "http://dl-learner.org/carcinogenesis#isMutagenic"
KG = RDFLoader("samples/mutag/mutag.owl", label_predicates=[LABEL_PREDICATE])
LEAKY_KG = RDFLoader("samples/mutag/mutag.owl", label_predicates=[])
TRAIN_DF = pd.read_csv("samples/mutag/train.tsv", sep="\t", header=0)
ENTITIES = [rdflib.URIRef(x) for x in TRAIN_DF["bond"]]
ENTITIES_SUBSET = ENTITIES[:5]

T = TypeVar("T")


def _get_classes() -> List[Tuple[str, T]]:
    """Gets the classes from a package.

    Returns:
        The classes from a package.

    """
    classes = []
    base_path = [os.path.dirname(pyrdf2vec.__file__)]
    print(base_path)
    for _, name, _ in pkgutil.walk_packages(
        path=base_path, prefix="pyrdf2vec."
    ):
        module = __import__(name, fromlist="dummy")
        classes.extend(inspect.getmembers(module, inspect.isclass))
    return classes


def _get_samplers() -> List[Tuple[str, T]]:
    """Gets the classes that are not a subclass of `sklearn.BaseEstimator` and
    that are not an abstract class.

    Returns:
        The classes.

    """
    classes = [  # type: ignore
        c  # type: ignore
        for c in set(_get_classes())  # type: ignore
        if issubclass(c[1], Sampler)  # type: ignore
    ]
    classes = filter(lambda c: not is_abstract(c[1]), classes)  # type: ignore
    return sorted(set(classes), key=itemgetter(0))


def check_sampler(Sampler):
    canonical_walks = RandomWalker(2, 5, Sampler()).extract(
        KG, ENTITIES_SUBSET
    )
    assert type(canonical_walks) == set


def is_abstract(c) -> bool:
    """Tells whether a class is abstract or not.

    Args:
        c: The class has to determine if it is abstract or not.

    Returns:
        True if abstract class, False otherwise.

    """
    return (
        hasattr(c, "__abstractmethods__") and len(c.__abstractmethods__) != 0
    )


@pytest.mark.parametrize("name, Sampler", _get_samplers())
def test_samplers(name: str, Sampler: T):
    """Tests the estimators in tslearn."""
    print(f"Testing {name}")
    check_sampler(Sampler)