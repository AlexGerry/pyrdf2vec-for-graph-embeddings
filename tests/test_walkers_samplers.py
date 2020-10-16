import functools
import itertools
import random

import numpy as np
import pandas as pd
import pytest
import rdflib

from pyrdf2vec.graphs import RDFLoader
from pyrdf2vec.rdf2vec import RDF2VecTransformer

from pyrdf2vec.walkers import (  # isort: skip
    AnonymousWalker,
    CommunityWalker,
    HalkWalker,
    NGramWalker,
    RandomWalker,
    WalkletWalker,
    WeisfeilerLehmanWalker,
)
from pyrdf2vec.samplers import (  # isort: skip
    ObjPredFreqSampler,
    PredFreqSampler,
    UniformSampler,
    ObjFreqSampler,
    PageRankSampler,
)


np.random.seed(42)
random.seed(42)

LABEL_PREDICATES = ["http://dl-learner.org/carcinogenesis#isMutagenic"]
KG = RDFLoader("samples/mutag/mutag.owl", label_predicates=LABEL_PREDICATES)
TRAIN_DF = pd.read_csv("samples/mutag/train.tsv", sep="\t", header=0)
ENTITIES = [rdflib.URIRef(x) for x in TRAIN_DF["bond"]]
ENTITIES_SUBSET = ENTITIES[:5]


SAMPLER_CLASSES = {
    ObjFreqSampler: "Object Frequency",
    ObjPredFreqSampler: "Predicate-Object Frequency",
    PageRankSampler: "PageRank",
    PredFreqSampler: "Predicate Frequency",
    UniformSampler: "Uniform",
}

SAMPLERS = {
    **SAMPLER_CLASSES,
}

SAMPLERS.update(
    {
        functools.partial(samp, inverse=True): (  # type: ignore
            "Inverse %s" % desc
        )
        for samp, desc in SAMPLERS.items()
        if samp is not UniformSampler
    }
)

WALKER_CLASSES = {
    AnonymousWalker: "Anonymous",
    CommunityWalker: "Community",
    HalkWalker: "HALK",
    NGramWalker: "NGram",
    RandomWalker: "Random",
    WalkletWalker: "Walklet",
    WeisfeilerLehmanWalker: "Weisfeiler-Lehman",
}


class TestRDF2Vec:
    @pytest.mark.parametrize(
        "walker, sampler", itertools.product(WALKER_CLASSES, SAMPLERS)
    )
    def test_fit_transform_with_cbow(self, walker, sampler):
        transformer = RDF2VecTransformer(
            walkers=[walker(2, 5, sampler())], sg=0
        )
        assert transformer.fit_transform(KG, ENTITIES_SUBSET)

    @pytest.mark.parametrize(
        "walker, sampler", itertools.product(WALKER_CLASSES, SAMPLERS)
    )
    def test_fit_transform_with_skip_gram(self, walker, sampler):
        transformer = RDF2VecTransformer(
            walkers=[walker(2, 5, sampler())], sg=1
        )
        assert transformer.fit_transform(KG, ENTITIES_SUBSET)