import pytest

from hestia_earth.aggregation.utils.queries import _current_year
from hestia_earth.aggregation.utils.management import aggregated_dates


@pytest.mark.parametrize(
    'node,expected',
    [
        ({'startDate': '1992-06-21', 'endDate': '1992-06-21'}, {'startDate': '1990-01-01', 'endDate': '2009-12-31'}),
        ({'endDate': '1992-06-21'}, {'startDate': '1990-01-01', 'endDate': '2009-12-31'}),
        (
            {'startDate': '2010-01-01', 'endDate': '2010-06-01'},
            {'startDate': '2010-01-01', 'endDate': f"{_current_year()}-01-01"}
        ),
        (
            {'startDate': '2009-01-01', 'endDate': '2010-12-31'},
            {'startDate': '2010-01-01', 'endDate': f"{_current_year()}-01-01"}
        ),
    ]
)
def test_aggregated_dates(node: dict, expected: str):
    assert aggregated_dates(node) == expected
