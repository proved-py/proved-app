import os

from django.shortcuts import render
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
from pm4py.util import xes_constants
from pm4py.visualization.petrinet import factory as pn_vis_factory
from django.conf import settings

from proved.artifacts.uncertain_log import uncertain_log
from proved import xes_keys
from proved.artifacts.behavior_net import behavior_net
from proved.artifacts.behavior_graph import behavior_graph

from apps.upload_eventlog import views as upload_log_page
from apps.upload_petrinet import views as upload_net_page


def alignments_home(request):
    if settings.EVENT_LOG_NAME == ':notset:':
        return upload_log_page.upload_page(request, target_page='/alignments')
    if settings.PETRI_NET_NAME == ':notset:':
        return upload_net_page.upload_page(request, target_page='/alignments')
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
    log_name = settings.EVENT_LOG_NAME.split('.')[0]
    log = xes_importer_factory.apply(event_log)
    u_log = uncertain_log.UncertainLog(log)
    variants_table = tuple((id_var, size, len(nodes_tuple) // 2) for id_var, (size, nodes_tuple) in u_log.variants.items())
    request.session['uncertainty_summary'] = {'variants': variants_table}
    return render(request, 'alignments_home.html', {'log_name': log_name, 'variants': variants_table})


def best_alignment(request, variant):
    if settings.EVENT_LOG_NAME == ':notset:':
        return upload_log_page.upload_page(request, target_page='/alignments')
    if settings.PETRI_NET_NAME == ':notset:':
        return upload_net_page.upload_page(request, target_page='/alignments')
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
    log_name = settings.EVENT_LOG_NAME.split('.')[0]
    log = xes_importer_factory.apply(event_log)
    u_log = uncertain_log.UncertainLog(log)
    variants_table = tuple((id_var, size, len(nodes_tuple) // 2) for id_var, (size, nodes_tuple) in u_log.variants.items())
    request.session['uncertainty_summary'] = {'variants': variants_table}
    return render(request, 'best_alignment.html', {'log_name': log_name, 'variants': variants_table})
