# coding: utf-8
from django.dispatch.dispatcher import Signal


#: Сигнал о начале этапа маршрута согласования.
route_phase_start = Signal(
    providing_args=('phase',),
)

#: Сигнал о завершении этапа маршрута согласования.
route_phase_change_state = Signal(
    providing_args=('phase', 'src_state', 'dst_state'),
)
