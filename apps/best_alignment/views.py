import os
import glob
from pathlib import Path

from django.shortcuts import render
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
from pm4py.util import xes_constants
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.objects.petri.importer import factory as pnml_importer
from pm4py.objects.petri.exporter import factory as pnml_exporter
from django.conf import settings

from proved.algorithms.conformance.alignments.alignment_bounds_su import alignment_lower_bound_su_trace, alignment_upper_bound_su_trace_bruteforce
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
    bg, _ = u_log.behavior_graphs_map[u_log.variants[variant][1]]
    bn = behavior_net.BehaviorNet(bg)
    if not glob.glob(os.path.join('static', 'dashboard', log_name, 'variants', 'img_bn', 'bn' + str(variant) + '.png')):
        bn = behavior_net.BehaviorNet(bg)
        gviz = pn_vis_factory.apply(bn, bn.initial_marking, bn.final_marking, parameters={'format': 'png'})
        Path(os.path.join('static', 'dashboard', log_name, 'variants', 'img_bn')).mkdir(parents=True, exist_ok=True)
        pn_vis_factory.save(gviz, os.path.join('static', 'dashboard', log_name, 'variants', 'img_bn', 'bn' + str(variant) + '.png'))
    image_bn = os.path.join('dashboard', log_name, 'variants', 'img_bn', 'bn' + str(variant) + '.png')
    petri_nets_path = os.path.join(settings.MEDIA_ROOT, "petri_nets")
    petri_net = os.path.join(petri_nets_path, settings.PETRI_NET_NAME)
    net, initial_marking, final_marking = pnml_importer.apply(petri_net)
    if not glob.glob(os.path.join('static', 'petri_nets', settings.PETRI_NET_NAME + '.png')):
        gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters={'format': 'png'})
        Path(os.path.join('static', 'petri_nets')).mkdir(parents=True, exist_ok=True)
        pn_vis_factory.save(gviz, os.path.join('static', 'petri_nets', settings.PETRI_NET_NAME + '.png'))
    image_model = os.path.join('petri_nets', settings.PETRI_NET_NAME + '.png')
    align_lower_bound = alignment_lower_bound_su_trace(bn, bn.initial_marking, bn.final_marking, net, initial_marking, final_marking)
    align_upper_bound, real_set_size = alignment_upper_bound_su_trace_bruteforce(bn, bn.initial_marking, bn.final_marking, net, initial_marking, final_marking)
    cost_lower_bound = align_lower_bound['cost'] // 10000
    cost_upper_bound = align_upper_bound['cost'] // 10000
    # align_lower_bound = [[item1, item2] for item1, item2 in align_lower_bound['alignment']], align_lower_bound['cost'] // 10000
    # align_upper_bound = [[item1, item2] for item1, item2 in align_upper_bound['alignment']], align_upper_bound['cost'] // 10000
    lower_bound_logmoves = [item[0] for item in align_lower_bound['alignment']]
    lower_bound_modelmoves = [item[1] for item in align_lower_bound['alignment']]
    upper_bound_logmoves = [item[0] for item in align_upper_bound['alignment']]
    upper_bound_modelmoves = [item[1] for item in align_upper_bound['alignment']]
    for i in range(len(lower_bound_logmoves)):
        if not lower_bound_logmoves[i]:
            lower_bound_logmoves[i] = '𝜏'
        if not lower_bound_modelmoves[i]:
            lower_bound_modelmoves[i] = '𝜏'
    for i in range(len(upper_bound_logmoves)):
        if not upper_bound_logmoves[i]:
            upper_bound_logmoves[i] = '𝜏'
        if not upper_bound_modelmoves[i]:
            upper_bound_modelmoves[i] = '𝜏'
    # for i in range(len(align_lower_bound[0])):
    #     if not align_lower_bound[0][i][0]:
    #         align_lower_bound[0][i][0] = '𝜏'
    #     if not align_lower_bound[0][i][1]:
    #         align_lower_bound[0][i][1] = '𝜏'
    # for i in range(len(align_upper_bound[0])):
    #     if not align_upper_bound[0][i][0]:
    #         align_upper_bound[0][i][0] = '𝜏'
    #     if not align_upper_bound[0][i][1]:
    #         align_upper_bound[0][i][1] = '𝜏'
    return render(request, 'best_alignment.html', {'log_name': log_name, 'variants': variants_table, 'image_bn': image_bn, 'image_model': image_model, 'cost_lower_bound': cost_lower_bound, 'cost_upper_bound': cost_upper_bound, 'lower_bound_logmoves': lower_bound_logmoves, 'lower_bound_modelmoves': lower_bound_modelmoves, 'upper_bound_logmoves': upper_bound_logmoves, 'upper_bound_modelmoves': upper_bound_modelmoves, 'real_set_size': real_set_size})
