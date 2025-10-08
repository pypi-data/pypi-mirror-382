# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Northwestern University.
#
# invenio-analytics-importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import pytest

from invenio_analytics_importer.convert import (
    generate_download_analytics,
    generate_view_analytics,
)


@pytest.fixture
def download_analytics_raw():
    """Raw Matamo analytics entry."""
    return (
        "2024-08-30",
        {
            "label": "prism.northwestern.edu/records/3s45v-k5m55/files/coffee.assess.bmi.gz?download=1",  # noqa
            "nb_hits": 5,
            "nb_uniq_visitors": 2,
            "nb_visits": 3,
            "sum_time_spent": 0,
        },
    )


def test_generate_download_analytics(download_analytics_raw):
    analytics = list(generate_download_analytics([download_analytics_raw]))
    entry = analytics[0]

    assert "3s45v-k5m55" == entry.pid
    assert "coffee.assess.bmi.gz" == entry.file_key
    assert 3 == entry.visits
    assert 5 == entry.views
    assert "2024-08-30" == entry.year_month_day


@pytest.fixture
def view_analytics_raw():
    """Raw Matamo view analytics entry."""
    return (
        "2024-08-30",
        {
            "avg_page_load_time": 1.904,
            "avg_time_dom_completion": 0.629,
            "avg_time_dom_processing": 0.412,
            "avg_time_network": 0.473,
            "avg_time_on_page": 454,
            "avg_time_server": 0.294,
            "avg_time_transfer": 0.096,
            "bounce_rate": "100%",
            "entry_bounce_count": "1",
            "entry_nb_actions": "1",
            "entry_nb_uniq_visitors": 1,
            "entry_nb_visits": "1",
            "entry_sum_visit_length": "0",
            "exit_nb_uniq_visitors": 1,
            "exit_nb_visits": "2",
            "exit_rate": "67%",
            "label": "/records/3s45v-k5m55",
            "max_time_dom_completion": "0.6440",
            "max_time_dom_processing": "0.7940",
            "max_time_network": "1.3810",
            "max_time_server": "0.4350",
            "max_time_transfer": "0.1760",
            "min_time_dom_completion": "0.6130",
            "min_time_dom_processing": "0.2180",
            "min_time_network": "0.0000",
            "min_time_server": "0.0020",
            "min_time_transfer": "0.0020",
            "nb_hits": 4,
            "nb_hits_following_search": "3",
            "nb_hits_with_time_dom_completion": "2",
            "nb_hits_with_time_dom_processing": "4",
            "nb_hits_with_time_network": "4",
            "nb_hits_with_time_server": "4",
            "nb_hits_with_time_transfer": "4",
            "nb_uniq_visitors": 1,
            "nb_visits": 3,
            "sum_time_spent": 1817,
        },
    )


def test_generate_view_analytics(view_analytics_raw):
    analytics = list(generate_view_analytics([view_analytics_raw]))
    entry = analytics[0]

    assert "3s45v-k5m55" == entry.pid
    assert 3 == entry.visits
    assert 4 == entry.views
    assert "2024-08-30" == entry.year_month_day
