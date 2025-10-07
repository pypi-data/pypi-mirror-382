import os
import json
import shutil
import pytest
from unittest.mock import Mock, patch
from hestia_earth.utils.model import find_primary_product
from hestia_earth.schema import TermTermType

from tests.utils import (
    fixtures_path, start_year, end_year, current_date, SOURCE, WORLD,
    overwrite_expected, order_results, fake_aggregated_version, fake_download
)
from hestia_earth.aggregation.aggregate_cycles import run_aggregate
from hestia_earth.aggregation.recalculate_cycles import should_recalculate, recalculate
from hestia_earth.aggregation.utils.distribution import (
    _nb_iterations, generate_blank_node_distribution, sample_weighted_distributions
)
from hestia_earth.aggregation.utils.quality_score import calculate_score

class_path = 'hestia_earth.aggregation.aggregate_cycles'
fixtures_folder = os.path.join(fixtures_path, 'cycle')

_files = [
    f for f in os.listdir(fixtures_folder)
    if os.path.isfile(os.path.join(fixtures_folder, f)) and f.endswith('.jsonld')
]


def _node_id(node: dict): return node.get('@id') or node.get('id')


def fake_download_site(cycles: list):
    def download(site: dict, **kwargs):
        return next((c.get('site') for c in cycles if _node_id(c.get('site')) == _node_id(site)), None)
    return download


def _fake_download_term(term_id: str, term_type: str):
    term_type_units = {
        TermTermType.STANDARDSLABELS.value: '% area',
        TermTermType.WATERREGIME.value: '% area',
        TermTermType.LANDCOVER.value: '% area',
        TermTermType.TILLAGE.value: '% area',
        TermTermType.LANDUSEMANAGEMENT.value: '% area',
        TermTermType.CROPRESIDUEMANAGEMENT.value: '%'
    }
    units = term_type_units.get(term_type)
    return {
        '@type': 'Term',
        '@id': term_id,
        'termType': term_type
    } | ({'units': units} if units else {})


def _fake_update_version(version: str, data: dict, *args):
    return data


def _fake_sample_indexes(values: list): return [i % len(values) for i in range(_nb_iterations())]


def _fake_sample_values(values: list, nb_iterations): return sorted(values[0:nb_iterations])


def _fake_truncated_normal_1d(shape, mu, **kwargs):
    return [[mu] * shape[1]]


@pytest.mark.parametrize('filename', _files)
@patch('hestia_earth.orchestrator.strategies.merge.merge_node.update_node_version', side_effect=_fake_update_version)
@patch('hestia_earth.orchestrator.strategies.merge.merge_list.update_node_version', side_effect=_fake_update_version)
@patch('hestia_earth.models.cycle.input.hestiaAggregatedData.run', return_value=[])
@patch('hestia_earth.aggregation.aggregate_cycles.remove_covariance_files', return_value=[])
@patch('hestia_earth.aggregation.aggregate_cycles.generate_covariance_country', return_value={})
@patch('hestia_earth.aggregation.utils.blank_node.download_term', side_effect=_fake_download_term)
@patch('hestia_earth.aggregation.utils.distribution._sample_indexes', side_effect=_fake_sample_indexes)
@patch('hestia_earth.aggregation.utils.distribution._sample_values', side_effect=_fake_sample_values)
@patch('hestia_earth.aggregation.utils.distribution.truncated_normal_1d', side_effect=_fake_truncated_normal_1d)
@patch('hestia_earth.aggregation.utils.cycle._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.site._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.site._aggregated_node', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.cycle._aggregated_node', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.practice.download_hestia', side_effect=fake_download)
@patch('hestia_earth.aggregation.utils.queries.download_hestia', side_effect=fake_download)
@patch('hestia_earth.aggregation.utils.term.download_hestia', side_effect=fake_download)
@patch('hestia_earth.aggregation.utils.management._current_date', return_value=current_date)
@patch('hestia_earth.aggregation.utils.queries._current_date', return_value=current_date)
@patch('hestia_earth.aggregation.utils.cycle._timestamp', return_value='')
@patch(
    'hestia_earth.aggregation.utils.aggregate_weighted.sample_weighted_distributions',
    side_effect=lambda *args: sorted(sample_weighted_distributions(*args))
)
@patch(
    'hestia_earth.aggregation.utils.aggregate_country_nodes.generate_blank_node_distribution',
    side_effect=lambda *args: sorted(generate_blank_node_distribution(*args))
)
@patch('hestia_earth.aggregation.utils.covariance._covariance_dir')
@patch('hestia_earth.aggregation.utils.aggregate_country_nodes.download_site')
@patch('hestia_earth.aggregation.utils.aggregate_country_nodes.download_nodes')
@patch(f"{class_path}.find_country_nodes")
def test_aggregate_country(
    mock_find_nodes: Mock,
    mock_download_nodes: Mock,
    mock_download_site: Mock,
    mock_covariance_dir: Mock,
    mock_1: Mock,
    mock_2: Mock,
    mock_3: Mock,
    mock_4: Mock,
    mock_5: Mock,
    mock_6: Mock,
    mock_7: Mock,
    mock_8: Mock,
    mock_9: Mock,
    mock_10: Mock,
    mock_11: Mock,
    mock_12: Mock,
    mock_13: Mock,
    mock_14: Mock,
    mock_15: Mock,
    mock_16: Mock,
    mock_17: Mock,
    mock_18: Mock,
    mock_19: Mock,
    mock_20: Mock,
    mock_21: Mock,
    filename: str
):
    filepath = os.path.join(fixtures_folder, filename)

    covariance_folder = os.path.join(fixtures_folder, 'covariance', filename.split('.')[0])
    os.makedirs(covariance_folder, exist_ok=True)

    with open(filepath, encoding='utf-8') as f:
        cycles = json.load(f)

    mock_find_nodes.return_value = [{'@id': c.get('@id')} for c in cycles]
    mock_download_site.side_effect = fake_download_site(cycles)

    def fake_download_nodes(nodes: list):
        ids = [n.get('@id') for n in nodes]
        return [c for c in cycles if c.get('@id') in ids]

    mock_download_nodes.side_effect = fake_download_nodes

    mock_covariance_dir.return_value = covariance_folder

    expected_filepath = os.path.join(fixtures_folder, 'country', filename)
    with open(expected_filepath, encoding='utf-8') as f:
        expected = json.load(f)

    product = find_primary_product(cycles[0])['term']
    country = cycles[0]['site']['country']

    results, *args = run_aggregate(
        country=country,
        product=product,
        start_year=start_year,
        end_year=end_year,
        source=SOURCE
    )
    results = [
        recalculate(agg, product) for agg in results
    ] if should_recalculate(product) else results
    results = list(map(calculate_score, results))
    shutil.rmtree(covariance_folder)
    overwrite_expected(expected_filepath, results)
    assert order_results(results) == expected


@pytest.mark.parametrize('filename', _files)
@patch('hestia_earth.aggregation.aggregate_cycles.generate_covariance_country', return_value={})
@patch('hestia_earth.aggregation.utils.distribution._sample_values', side_effect=_fake_sample_values)
@patch('hestia_earth.aggregation.utils.distribution.truncated_normal_1d', side_effect=_fake_truncated_normal_1d)
@patch('hestia_earth.aggregation.utils.cycle._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.site._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.site._aggregated_node', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.cycle._aggregated_node', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.practice.download_hestia', side_effect=fake_download)
@patch('hestia_earth.aggregation.utils.queries.download_hestia', side_effect=fake_download)
@patch('hestia_earth.aggregation.utils.term.download_hestia', side_effect=fake_download)
@patch('hestia_earth.aggregation.utils.management._current_date', return_value=current_date)
@patch('hestia_earth.aggregation.utils.queries._current_date', return_value=current_date)
@patch('hestia_earth.aggregation.utils.cycle._timestamp', return_value='')
@patch(f"{class_path}.download_site")
@patch(f"{class_path}.find_global_nodes")
def test_aggregate_global(
    mock_find_nodes: Mock,
    mock_download_site: Mock,
    mock_1: Mock,
    mock_2: Mock,
    mock_3: Mock,
    mock_4: Mock,
    mock_5: Mock,
    mock_6: Mock,
    mock_7: Mock,
    mock_8: Mock,
    mock_9: Mock,
    mock_10: Mock,
    mock_11: Mock,
    mock_12: Mock,
    mock_13: Mock,
    filename: str
):
    filepath = os.path.join(fixtures_folder, 'country', filename)
    with open(filepath, encoding='utf-8') as f:
        cycles = json.load(f)

    mock_find_nodes.return_value = cycles
    mock_download_site.side_effect = fake_download_site(cycles)

    expected_filepath = os.path.join(fixtures_folder, 'global', filename)
    with open(expected_filepath, encoding='utf-8') as f:
        expected = json.load(f)

    product = find_primary_product(cycles[0])['term']

    results, countries = run_aggregate(
        country=WORLD,
        product=product,
        start_year=start_year,
        end_year=end_year,
        source=SOURCE
    )
    results = [calculate_score(r, countries) for r in results]
    overwrite_expected(expected_filepath, results)
    assert order_results(results) == expected
