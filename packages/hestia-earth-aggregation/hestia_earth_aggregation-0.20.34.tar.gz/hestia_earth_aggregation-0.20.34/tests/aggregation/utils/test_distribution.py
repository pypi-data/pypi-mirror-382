import pytest
from hestia_earth.schema import TermTermType

from hestia_earth.aggregation.utils.distribution import (
    _nb_iterations,
    generate_distribution,
    generate_blank_node_distribution,
    sample_distributions,
    sample_weighted_distributions,
    _distribute_iterations
)

_term = {'termType': TermTermType.MEASUREMENT.value, '@id': 'sandContent'}


@pytest.mark.parametrize(
    'value,sd,min,max',
    [
        (10, None, None, None),
        (10, 1, None, None),
        (10, 1, 5, None),
        (10, 1, None, 15),
        (10, None, 5, None),
        (10, None, None, 15),
        (0, None, None, None),
        (10, 0.1, 10, 10)
    ]
)
def test_generate_distribution(value: float, sd: float, min: float, max: float):
    results = generate_distribution(_term, value=value, min=min, max=max, sd=sd)
    assert len(results) == _nb_iterations()


@pytest.mark.parametrize(
    'blank_node',
    [
        ({
            'term': {'@id': 'n2OToAirCropResidueDecompositionDirect', 'termType': 'emission'},
            'value': [0.054105577868767914],
            'min': [0.009017596311461318],
            'max': [0.0991935594260745],
            'sd': [0.0005082315202280046]
        })
    ]
)
def test_generate_blank_node_distribution(blank_node: dict):
    results = generate_blank_node_distribution(blank_node)
    assert len(results) == _nb_iterations()


def test_sample_distributions():
    distributions = list(generate_distribution(_term, value=10)) * 10
    assert len(sample_distributions(distributions)) == _nb_iterations()


@pytest.mark.parametrize(
    'values',
    [
        ([
            ([100] * _nb_iterations(), 1 / 3),
            ([100] * _nb_iterations(), 1 / 3),
            ([100] * _nb_iterations(), 1 / 3),
        ]),
        ([([0, 0, 0, 0, 0, 0, 0, 0, 0.79915], 0.32653939141051624)]),
        ([([0] * _nb_iterations() + [10, 12], 0.5)])
    ]
)
def test_sample_weighted_distributions(values: list):
    distributions = sample_weighted_distributions(values)
    assert len(distributions) == _nb_iterations()


def test_distribute_iterations():
    assert _distribute_iterations([1] * 2, iterations=2) == [1, 1]
    assert _distribute_iterations([1] * 2, iterations=3) == [2, 1]
    assert _distribute_iterations([1] * 4, iterations=10) == [3, 3, 2, 2]
    assert _distribute_iterations([1] * 60, iterations=100) == [2] * 40 + [1] * 20
