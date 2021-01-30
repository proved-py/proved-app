from django.shortcuts import render
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
from pm4py.util import xes_constants
from pm4py.visualization.petrinet import factory as pn_vis_factory
from django.conf import settings
import os
import glob
import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from graphviz import Digraph
from datetime import datetime, timedelta
from io import BytesIO
import base64

from proved.artifacts.uncertain_log import uncertain_log
from proved import xes_keys
from proved.artifacts.behavior_net import behavior_net
from proved.artifacts.behavior_graph import behavior_graph

from apps.upload_eventlog import views as upload_log_page

# Create your views here.


def dashboard_home(request):
    if settings.EVENT_LOG_NAME == ':notset:':
        return upload_log_page.upload_page(request, target_page='dashboard.html')
        # return upload_log_page.upload_page(request, target_page='/dashboard/')
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
    log_name = settings.EVENT_LOG_NAME.split('.')[0]
    log = xes_importer_factory.apply(event_log)
    u_log = uncertain_log.UncertainLog(log)
    variants_table = tuple((id_var, size, len(nodes_tuple)//2) for id_var, (size, nodes_tuple) in u_log.variants.items())
    log_len = 0
    n_certain_events = 0
    n_uncertain_events = 0
    n_certain_traces = 0
    n_uncertain_traces = 0
    for trace in log:
        log_len += len(trace)
        is_trace_uncertain = False
        for event in trace:
            if xes_keys.DEFAULT_U_NAME_KEY in event or xes_keys.DEFAULT_U_TIMESTAMP_MIN_KEY in event or xes_keys.DEFAULT_U_MISSING_KEY in event:
                n_uncertain_events += 1
                is_trace_uncertain = True
            else:
                n_certain_events += 1
        if is_trace_uncertain:
            n_uncertain_traces += 1
        else:
            n_certain_traces += 1
    labels = ['Certain', 'Uncertain']
    colors = ['lightblue', 'lightsteelblue']
    explode = [0, .1]
    patches, texts = plt.pie([n_certain_events, n_uncertain_events], colors=colors, shadow=True, startangle=90, explode=explode, labels=[str(n_certain_events) + '\n(' + str(round(n_certain_events / (n_certain_events + n_uncertain_events) * 100, 2)) + '%)', str(n_uncertain_events) + '\n(' + str(round(n_uncertain_events / (n_certain_events + n_uncertain_events) * 100, 2)) + '%)'])
    plt.legend(patches, labels, loc="best")
    plt.axis('equal')
    plt.tight_layout()
    event_ratio_graph = os.path.join('dashboard', log_name, 'event_ratio.png')
    Path(os.path.join('static', 'dashboard', log_name)).mkdir(parents=True, exist_ok=True)
    plt.savefig(os.path.join('static', event_ratio_graph))
    plt.clf()
    patches, texts = plt.pie([n_certain_traces, n_uncertain_traces], colors=colors, shadow=True, startangle=90, explode=explode, labels=[str(n_certain_traces) + '\n(' + str(round(n_certain_traces / (n_certain_traces + n_uncertain_traces) * 100, 2)) + '%)', str(n_uncertain_traces) + '\n(' + str(round(n_uncertain_traces / (n_certain_traces + n_uncertain_traces) * 100, 2)) + '%)'])
    plt.legend(patches, labels, loc="best")
    plt.axis('equal')
    plt.tight_layout()
    trace_ratio_graph = os.path.join('dashboard', log_name, 'trace_ratio.png')
    plt.savefig(os.path.join('static', trace_ratio_graph))
    plt.clf()
    avg_trace_len = log_len / len(log)
    activities_map = dict()
    start_activities_map = dict()
    end_activities_map = dict()
    for _, (_, nodes_lists) in u_log.variants.items():
        for ((_, activities), _) in nodes_lists:
            for activity in activities:
                if activity is not None:
                    activities_map[activity] = [0, 0]
                    start_activities_map[activity] = [0, 0]
                    end_activities_map[activity] = [0, 0]
    for trace in log:
        for i, event in enumerate(trace):
            if xes_keys.DEFAULT_U_NAME_KEY in event:
                for activity in event[xes_keys.DEFAULT_U_NAME_KEY]['children']:
                    activities_map[activity][1] += 1
                    if i == 0:
                        start_activities_map[activity][1] += 1
                    if i == len(trace) - 1:
                        end_activities_map[activity][1] += 1
            elif xes_keys.DEFAULT_U_MISSING_KEY in event:
                activities_map[event[xes_constants.DEFAULT_NAME_KEY]][1] += 1
                if i == 0:
                    start_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][1] += 1
                if i == len(trace) - 1:
                    end_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][1] += 1
            else:
                activities_map[event[xes_constants.DEFAULT_NAME_KEY]][0] += 1
                activities_map[event[xes_constants.DEFAULT_NAME_KEY]][1] += 1
                if i == 0:
                    start_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][0] += 1
                    start_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][1] += 1
                if i == len(trace) - 1:
                    end_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][0] += 1
                    end_activities_map[event[xes_constants.DEFAULT_NAME_KEY]][1] += 1
    activities_table_abs = sorted([(freq_min, freq_max, activity) for activity, [freq_min, freq_max] in activities_map.items()], reverse=True)
    start_activities_table_abs = sorted([(freq_min, freq_max, activity) for activity, [freq_min, freq_max] in start_activities_map.items()], reverse=True)
    end_activities_table_abs = sorted([(freq_min, freq_max, activity) for activity, [freq_min, freq_max] in end_activities_map.items()], reverse=True)
    activities_table = [(freq_min, freq_max, round(freq_min/log_len*100, 2), round(freq_max/log_len*100, 2), activity) for freq_min, freq_max, activity in activities_table_abs]
    start_activities_table = [(freq_min, freq_max, round(freq_min/log_len*100, 2), round(freq_max/log_len*100, 2), activity) for freq_min, freq_max, activity in start_activities_table_abs]
    end_activities_table = [(freq_min, freq_max, round(freq_min/log_len*100, 2), round(freq_max/log_len*100, 2), activity) for freq_min, freq_max, activity in end_activities_table_abs]
    request.session['uncertainty_summary'] = {'variants': variants_table, 'log_len': log_len, 'avg_trace_len': avg_trace_len, 'activities_table': activities_table, 'start_activities_table': start_activities_table, 'end_activities_table': end_activities_table}
    print('00000000000000000000000000000000000000000000000000000' + str(variants_table))
    return render(request, 'dashboard.html', {'variants': variants_table, 'log': log, 'log_len': log_len, 'avg_trace_len': avg_trace_len, 'activities_table': activities_table, 'start_activities_table': start_activities_table, 'end_activities_table': end_activities_table, 'event_ratio_graph': event_ratio_graph, 'trace_ratio_graph': trace_ratio_graph})


def dashboard_variant(request, variant):
    if settings.EVENT_LOG_NAME == ':notset:':
        return upload_log_page.upload_page(request, target_page='dashboard_variant.html')
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
    log_name = settings.EVENT_LOG_NAME.split('.')[0]
    log = xes_importer_factory.apply(event_log)
    u_log = uncertain_log.UncertainLog(log)
    variants_table = request.session['uncertainty_summary']['variants']
    bg, traces_list = u_log.behavior_graphs_map[u_log.variants[variant][1]]
    traces_table = ((i, len(trace)) for i, trace in enumerate(traces_list))
    # Path(os.path.join(settings.STATIC_URL, 'dashboard', 'variant', 'img_bn', log_name)).mkdir(parents=True, exist_ok=True)
    if not glob.glob(os.path.join(settings.STATIC_URL, 'dashboard', log_name, 'variants', 'img_bg', 'bg' + str(variant) + '.png')):
        g = Digraph('bg', format='png', filename='bg' + str(variant) + '.png')
        g.attr(rankdir='LR')
        for bg_node in bg.nodes:
            if None in bg_node[1]:
                g.attr('node', style='dashed')
            else:
                g.attr('node', style='solid')
            g.node(''.join([act.replace(' ', '').replace(':', '') for act in bg_node[1] if act is not None]) + str(bg_node[0]), label=', '.join([act for act in bg_node[1] if act is not None]))
        for bg_node1, bg_node2 in bg.edges:
            g.edge(''.join([act.replace(' ', '').replace(':', '') for act in bg_node1[1] if act is not None]) + str(bg_node1[0]), ''.join([act.replace(' ', '').replace(':', '') for act in bg_node2[1] if act is not None]) + str(bg_node2[0]))
        bg_render = g.render(cleanup=True)
        image_bg = os.path.join('dashboard', log_name, 'variants', 'img_bg', 'bg' + str(variant) + '.png')
        Path(os.path.join('static', 'dashboard', log_name, 'variants', 'img_bg')).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bg_render, os.path.join('static', image_bg))
    image_bg = os.path.join('dashboard', log_name, 'variants', 'img_bg', 'bg' + str(variant) + '.png')
    if not glob.glob(os.path.join(settings.STATIC_URL, 'dashboard', log_name, 'variants', 'img_bn', 'bn' + str(variant) + '.png')):
        bn = behavior_net.BehaviorNet(bg)
        gviz = pn_vis_factory.apply(bn, bn.initial_marking, bn.final_marking, parameters={'format': 'png'})
        Path(os.path.join('static', 'dashboard', log_name, 'variants', 'img_bn')).mkdir(parents=True, exist_ok=True)
        pn_vis_factory.save(gviz, os.path.join('static', 'dashboard', log_name, 'variants', 'img_bn', 'bn' + str(variant) + '.png'))
    image_bn = os.path.join('dashboard', log_name, 'variants', 'img_bn', 'bn' + str(variant) + '.png')
    return render(request, 'dashboard_variant.html', {'variant': variant, 'variants': variants_table, 'traces': traces_table, 'log_name': log_name, 'image_bn': image_bn, 'image_bg': image_bg})


def dashboard_trace(request, variant, trace):
    if settings.EVENT_LOG_NAME == ':notset:':
        return upload_log_page.upload_page(request, target_page='dashboard_trace.html')
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
    log_name = settings.EVENT_LOG_NAME.split('.')[0]
    log = xes_importer_factory.apply(event_log)
    u_log = uncertain_log.UncertainLog(log)
    variants_table = request.session['uncertainty_summary']['variants']
    bg, traces_list = u_log.behavior_graphs_map[u_log.variants[variant][1]]
    traces_table = ((i, len(trace)) for i, trace in enumerate(traces_list))
    # Path(os.path.join(settings.STATIC_URL, 'dashboard', 'variant', 'img_bn', log_name)).mkdir(parents=True, exist_ok=True)
    if not glob.glob(os.path.join(settings.STATIC_URL, 'dashboard', log_name, 'variants', 'img_bg', 'bg' + str(variant) + '.png')):
        g = Digraph('bg', format='png', filename='bg' + str(variant) + '.png')
        g.attr(rankdir='LR')
        for bg_node in bg.nodes:
            if None in bg_node[1]:
                g.attr('node', style='dashed')
            else:
                g.attr('node', style='solid')
            g.node(''.join([act.replace(' ', '').replace(':', '') for act in bg_node[1] if act is not None]) + str(bg_node[0]), label=', '.join([act for act in bg_node[1] if act is not None]))
        for bg_node1, bg_node2 in bg.edges:
            g.edge(''.join([act.replace(' ', '').replace(':', '') for act in bg_node1[1] if act is not None]) + str(bg_node1[0]), ''.join([act.replace(' ', '').replace(':', '') for act in bg_node2[1] if act is not None]) + str(bg_node2[0]))
        bg_render = g.render(cleanup=True)
        image_bg = os.path.join('dashboard', log_name, 'variants', 'img_bg', 'bg' + str(variant) + '.png')
        Path(os.path.join('static', 'dashboard', log_name, 'variants', 'img_bg')).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bg_render, os.path.join('static', image_bg))
    image_bg = os.path.join('dashboard', log_name, 'variants', 'img_bg', 'bg' + str(variant) + '.png')
    if not glob.glob(os.path.join(settings.STATIC_URL, 'dashboard', log_name, 'variants', 'img_bn', 'bn' + str(variant) + '.png')):
        bn = behavior_net.BehaviorNet(bg)
        gviz = pn_vis_factory.apply(bn, bn.initial_marking, bn.final_marking, parameters={'format': 'png'})
        Path(os.path.join('static', 'dashboard', log_name, 'variants', 'img_bn')).mkdir(parents=True, exist_ok=True)
        pn_vis_factory.save(gviz, os.path.join('static', 'dashboard', log_name, 'variants', 'img_bn', 'bn' + str(variant) + '.png'))
    image_bn = os.path.join('dashboard', log_name, 'variants', 'img_bn', 'bn' + str(variant) + '.png')
    trace_table = []
    for i, event in enumerate(traces_list[trace]):
        table_row = [str(i)]
        if xes_keys.DEFAULT_U_NAME_KEY in event:
            table_row.append(', '.join([str(act) for act in event[xes_keys.DEFAULT_U_NAME_KEY]['children']]))
        else:
            table_row.append(str(event[xes_constants.DEFAULT_NAME_KEY]))
        if xes_keys.DEFAULT_U_TIMESTAMP_MIN_KEY in event:
            table_row.append(str(event[xes_keys.DEFAULT_U_TIMESTAMP_MIN_KEY].strftime('%d-%m-%Y %H:%M:%S')))
            table_row.append(str(event[xes_keys.DEFAULT_U_TIMESTAMP_MAX_KEY].strftime('%d-%m-%Y %H:%M:%S')))
        else:
            table_row.append(str(event[xes_constants.DEFAULT_TIMESTAMP_KEY].strftime('%d-%m-%Y %H:%M:%S')))
            table_row.append(str(event[xes_constants.DEFAULT_TIMESTAMP_KEY].strftime('%d-%m-%Y %H:%M:%S')))
        if xes_keys.DEFAULT_U_MISSING_KEY in event:
            table_row.append('Yes')
        else:
            table_row.append('No')
        trace_table.append(table_row)
    fig, gnt = plt.subplots()
    dates = []
    labels = []
    for event in traces_list[trace]:
        if xes_keys.DEFAULT_U_TIMESTAMP_MIN_KEY in event:
            dates.append((mdates.date2num(event[xes_keys.DEFAULT_U_TIMESTAMP_MIN_KEY]), mdates.date2num(event[xes_keys.DEFAULT_U_TIMESTAMP_MAX_KEY]) - mdates.date2num(event[xes_keys.DEFAULT_U_TIMESTAMP_MIN_KEY])))
        else:
            dates.append((mdates.date2num(event[xes_constants.DEFAULT_TIMESTAMP_KEY]), mdates.date2num(event[xes_constants.DEFAULT_TIMESTAMP_KEY] + timedelta(hours=1)) - mdates.date2num(event[xes_constants.DEFAULT_TIMESTAMP_KEY])))
        if xes_keys.DEFAULT_U_NAME_KEY in event:
            labels.append(', '.join([str(act) for act in event[xes_keys.DEFAULT_U_NAME_KEY]['children']]))
        else:
            labels.append(str(event[xes_constants.DEFAULT_NAME_KEY]))
    gnt.set_ylim(0, len(dates) * 10 + 20)
    gnt.set_yticks([i * 10 + 15 for i in range(len(dates))])
    gnt.set_yticklabels(labels)
    gnt.grid(True)
    for i, (base, increment) in enumerate(dates):
        gnt.broken_barh([(base, increment)], ((i + 1) * 10, 9), facecolors=('tab:blue'))
    # gnt.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M:%S'))
    gnt.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    fig.autofmt_xdate()
    Path(os.path.join('static', 'dashboard', log_name, 'traces', 'img_gantt')).mkdir(parents=True, exist_ok=True)
    plt.savefig(os.path.join('static', 'dashboard', log_name, 'traces', 'img_gantt', 'gantt' + str(variant) + '_' + str(trace) + '.png'), bbox_inches='tight')
    plt.savefig(os.path.join('static', 'dashboard', log_name, 'traces', 'img_gantt', 'gantt' + str(variant) + '_' + str(trace) + '.pdf'), bbox_inches='tight')
    plt.clf()
    image_gantt = os.path.join('dashboard', log_name, 'traces', 'img_gantt', 'gantt' + str(variant) + '_' + str(trace) + '.png')
    return render(request, 'dashboard_trace.html', {'variant': variant, 'trace': trace, 'trace_table': trace_table,  'variants': variants_table, 'traces': traces_table, 'log_name': log_name, 'image_bn': image_bn, 'image_bg': image_bg, 'image_gantt': image_gantt})
