# -*- coding: utf-8 -*-

from brainiak import settings
from brainiak.prefixes import uri_to_slug
from brainiak.search_engine import run_search
from brainiak.utils import resources
from brainiak.utils.sparql import RDFS_LABEL


def do_search(query_params):

    search_fields = _get_search_fields()
    elasticsearch_result = do_search_query(query_params, search_fields)
    total_items = elasticsearch_result["hits"]["total"]
    if total_items:
        response_items = _build_items(elasticsearch_result)
    else:
        response_items = {}
    response = _build_json(response_items, total_items, query_params)

    return response


def do_search_query(query_params, search_fields, analyzer=settings.ES_ANALYZER):
    ELASTICSEARCH_QUERY_DICT = {
        "filter": {
            "type": {
                "value": query_params["class_uri"]
            }
        },
        "query": {
            "multi_match": {
                "query": "{0}".format(query_params["pattern"]),
                "fields": search_fields,
                "analyzer": analyzer,
                "fuzziness": 0.7  # based on manual tests
            },
        },
        "from": int(resources.calculate_offset(query_params)),
        "size": int(query_params.get("per_page", settings.DEFAULT_PER_PAGE)),
    }

    indexes = ["semantica." + uri_to_slug(query_params["graph_uri"])]
    elasticsearch_result = run_search(ELASTICSEARCH_QUERY_DICT, indexes=indexes)
    return elasticsearch_result


def _build_items(elasticsearch_result):
    items = []
    es_items = elasticsearch_result["hits"].get("hits", [])
    for item in es_items:
        item_dict = {
            "id": item["_id"],
            "title": item["_source"][RDFS_LABEL],
        }
        items.append(item_dict)

    return items


def _build_json(items_list, item_count, query_params):

    json = {
        '_base_url': query_params.base_url,
        'items': items_list,
        "@context": {"@language": query_params.get("lang")},
        "pattern": query_params["pattern"],
        # Variables needed for corresponding json-schema
        "_graph_uri": query_params["graph_uri"],
        "_class_prefix": query_params["class_prefix"],
        "_class_uri": query_params["class_uri"]
    }

    calculate_total_items = lambda: item_count
    resources.decorate_dict_with_pagination(json, query_params, calculate_total_items)

    return json


# TODO consider rdfs:label subproperties
def _get_search_fields():  # pragma: no cover
    return [RDFS_LABEL]
