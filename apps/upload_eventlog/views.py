from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
from django.conf import settings
import os
from os import listdir
from os.path import isfile, join
from django.http import HttpResponse
from wsgiref.util import FileWrapper


def upload_page(request, target_page=''):
    log_attributes = {}
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")

    if request.method == 'POST':
        if "targetPage" in request.POST:
            if request.POST['targetPage'] is not '':
                target_page = request.POST['targetPage']

        if "uploadButton" in request.POST:
            if "event_log" not in request.FILES:
                return HttpResponseRedirect(request.path_info)

            log = request.FILES["event_log"]
            fs = FileSystemStorage(event_logs_path)
            filename = fs.save(log.name, log)
            uploaded_file_url = fs.url(filename)

            eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

            file_dir = os.path.join(event_logs_path, filename)

            return render(request, 'upload_el.html', {'eventlog_list': eventlogs, 'target_page': target_page})

        elif "deleteButton" in request.POST:
            if "log_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)

            filename = request.POST["log_list"]
            if settings.EVENT_LOG_NAME == filename:
                settings.EVENT_LOG_NAME = ":notset:"

            eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

            eventlogs.remove(filename)
            file_dir = os.path.join(event_logs_path, filename)
            os.remove(file_dir)
            return render(request, 'upload_el.html', {'eventlog_list': eventlogs, 'target_page': target_page})

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

            if target_page == '':
                return render(request, target_page, {'eventlog_list': eventlogs, 'log_name': filename, 'log_attributes': log_attributes})
            else:
                return redirect(target_page)

        elif "downloadButton" in request.POST:
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
        return render(request, 'upload_el.html', {'eventlog_list': eventlogs, 'target_page': target_page})
