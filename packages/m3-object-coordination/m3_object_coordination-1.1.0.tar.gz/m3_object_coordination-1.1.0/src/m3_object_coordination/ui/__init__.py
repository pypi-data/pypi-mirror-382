# coding: utf-8
"""Реализация элементов интерфейса подсистемы согласования.

Содержит редактор шаблонов маршрутов согласования и грид маршрута согласования.
"""
from operator import itemgetter

from django.contrib.contenttypes.models import ContentType
from objectpack.models import VirtualModel

import m3_object_coordination

from ..utils import get_approover_types_for


class ApprooverType(VirtualModel):

    """Виртуальная модель с наименований типов объектов согласующих."""

    def __init__(self, data):  # noqa: D107
        self.id = data['id']
        self.name = data['name']
        self.column_name_on_select = data['column_name_on_select']
        self.select_window_url = data['select_window_url']

    @classmethod
    def _get_ids(cls, object_type: ContentType):  # pylint: disable=W0221
        data = []
        for approover_type, pack in get_approover_types_for(object_type):
            column_name_on_select = (
                pack.column_name_on_select if pack else ''
            )
            select_window_url = pack.select_window_action.get_absolute_url()
            data.append(
                dict(
                    id=approover_type.id,
                    name=approover_type.name,
                    column_name_on_select=column_name_on_select or '',
                    select_window_url=select_window_url,
                )
            )

        return sorted(data, key=itemgetter('name'))
