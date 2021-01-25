from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
from django.conf import settings
import os
from os import listdir
from os.path import isfile, join
from django.http import HttpResponse
from wsgiref.util import FileWrapper
import json


# Create your views here.

def upload_page(request):
    log_attributes = {}
    event_logs_path = os.path.join(settings.MEDIA_ROOT,"event_logs")
    n_event_logs_path = os.path.join(settings.MEDIA_ROOT,"none_event_logs")

    if request.method == 'POST':
        if request.is_ajax():  # currently is not being used (get commented in html file)
            filename = request.POST["log_name"]
            print('filename = ', filename)
            file_dir = os.path.join(event_logs_path, filename)
            eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

            xes_log = xes_importer_factory.apply(file_dir)
            no_traces = len(xes_log)
            no_events = sum([len(trace) for trace in xes_log])
            log_attributes['no_traces'] = no_traces
            log_attributes['no_events'] = no_events
            print(log_attributes)
            json_respone = {'log_attributes': log_attributes, 'eventlog_list':eventlogs}
            return HttpResponse(json.dumps(json_respone),content_type='application/json')
        else:
            if "uploadButton" in request.POST:
                if "event_log" not in request.FILES:
                    return HttpResponseRedirect(request.path_info)

                log = request.FILES["event_log"]
                fs = FileSystemStorage(event_logs_path)
                filename = fs.save(log.name, log)
                uploaded_file_url = fs.url(filename)

                eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

                file_dir = os.path.join(event_logs_path, filename)

                return render(request, 'upload.html', {'eventlog_list':eventlogs})

            elif "deleteButton" in request.POST: #for event logs
                if "log_list" not in request.POST:
                    return HttpResponseRedirect(request.path_info)

                filename = request.POST["log_list"]
                if settings.EVENT_LOG_NAME == filename:
                    settings.EVENT_LOG_NAME = ":notset:"

                eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]
                n_eventlogs = [f for f in listdir(n_event_logs_path) if isfile(join(n_event_logs_path, f))]

                eventlogs.remove(filename)
                file_dir = os.path.join(event_logs_path, filename)
                os.remove(file_dir)
                return render(request, 'upload.html',{'eventlog_list': eventlogs, 'n_eventlog_list': n_eventlogs})

            elif "setButton" in request.POST:
                if "log_list" not in request.POST:
                    return HttpResponseRedirect(request.path_info)

                filename = request.POST["log_list"]
                settings.EVENT_LOG_NAME = filename

                file_dir = os.path.join(event_logs_path, filename)

                xes_log = xes_importer_factory.apply(file_dir)
                no_traces = len(xes_log)
                no_events = sum([len(trace) for trace in xes_log])
                log_attributes['no_traces'] = no_traces
                log_attributes['no_events'] = no_events

                eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

                return render(request, 'upload.html',{'eventlog_list': eventlogs, 'log_name':filename, 'log_attributes':log_attributes})

            elif "downloadButton" in request.POST: #for event logs
                if "log_list" not in request.POST:
                    return HttpResponseRedirect(request.path_info)

                filename = request.POST["log_list"]
                file_dir = os.path.join(event_logs_path, filename)

                try:
                    wrapper = FileWrapper(open(file_dir, 'rb'))
                    response = HttpResponse(wrapper, content_type='application/force-download')
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_dir)
                    return response
                except Exception:
                    return None

    else:
        eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]
        n_eventlogs = [f for f in listdir(n_event_logs_path) if isfile(join(n_event_logs_path, f))]

        return render(request, 'upload.html', {'eventlog_list':eventlogs, 'n_eventlog_list': n_eventlogs})
