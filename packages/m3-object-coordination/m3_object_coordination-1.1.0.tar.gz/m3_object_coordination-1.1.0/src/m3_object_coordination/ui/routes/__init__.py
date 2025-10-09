# coding: utf-8
"""Реализация грида для работы с маршрутами согласования.

Предполагается, что грид будет встраиваться в окна редактирования согласуемых
объектов, либо использоваться в специализированных окнах.
"""
# pylint: disable=no-name-in-module
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution
from pkg_resources.extern.packaging.version import LegacyVersion
from pkg_resources.extern.packaging.version import Version


def _m3_ui_version_check():
    minimal_version = '2.2.57'

    try:
        distribution = get_distribution('m3-ui')
    except DistributionNotFound:
        pass
    else:
        if (
            not isinstance(distribution.parsed_version, LegacyVersion) and
            distribution.parsed_version < Version(minimal_version) and
            not distribution.parsed_version.is_prerelease
        ):
            raise AssertionError(
                f'm3-ui=={distribution.version} not supported.'
            )


_m3_ui_version_check()
