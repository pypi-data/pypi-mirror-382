# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Northwestern University.
#
# invenio-analytics-importer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Convert data from one format to another."""

import dataclasses
import re


@dataclasses.dataclass
class DownloadAnalytics:
    """Intermediate representation."""

    year_month_day: str  # keeping it simple for now
    pid: str
    file_key: str
    visits: int
    views: int

    @classmethod
    def create(cls, year_month_day, analytics_raw):
        """Create Entry from raw analytics."""
        label = analytics_raw.get("label", "")

        # extract "3s45v-k5m55" from ".../records/3s45v-k5m55[/...]"
        regex_pid = re.compile(r"/records/([^/]*)(?:/|$)")
        pid = regex_pid.search(label).group(1)

        # extract file key
        regex_key = re.compile(r"/files/([^?]*)\?download=1")
        file_key = regex_key.search(label).group(1)

        return cls(
            year_month_day=year_month_day,
            pid=pid,
            file_key=file_key,
            visits=analytics_raw.get("nb_visits", 0),
            views=analytics_raw.get("nb_hits", 0),
        )


def generate_download_analytics(raw_analytics):
    """Yield DownloadAnalytics entries from raw entries."""
    for year_month_day, raw in raw_analytics:
        yield DownloadAnalytics.create(year_month_day, raw)


@dataclasses.dataclass
class ViewAnalytics:
    """Intermediate representation of view analytics."""

    year_month_day: str  # keeping it simple for now
    pid: str
    visits: int
    views: int

    @classmethod
    def create(cls, year_month_day, analytics_raw):
        """Create from raw analytics."""
        label = analytics_raw.get("label", "")

        # extract "3s45v-k5m55" from ".../records/3s45v-k5m55[/...]"
        regex_pid = re.compile(r"/records/([^/]*)(?:/|$)")
        match = regex_pid.search(label)
        pid = match.group(1) if match else ""

        return cls(
            year_month_day=year_month_day,
            pid=pid,
            visits=analytics_raw.get("nb_visits", 0),
            views=analytics_raw.get("nb_hits", 0),
        )


def generate_view_analytics(raw_analytics):
    """Yield ViewAnalytics entries from raw entries."""
    for year_month_day, raw in raw_analytics:
        yield ViewAnalytics.create(year_month_day, raw)
