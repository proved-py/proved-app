from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
import os
from os import listdir
from os.path import isfile, join
from django.http import HttpResponse
from wsgiref.util import FileWrapper


def upload_page(request, target_page=''):
    petri_nets_path = os.path.join(settings.MEDIA_ROOT, "petri_nets")

    if request.method == 'POST':
        if "targetPage" in request.POST:
            if request.POST['targetPage'] is not '':
                target_page = request.POST['targetPage']

        if "uploadButton" in request.POST:
            if "petri_net" not in request.FILES:
                return HttpResponseRedirect(request.path_info)

            net = request.FILES["petri_net"]
            fs = FileSystemStorage(petri_nets_path)
            filename = fs.save(net.name, net)
            uploaded_file_url = fs.url(filename)

            petrinets = [f for f in listdir(petri_nets_path) if isfile(join(petri_nets_path, f))]

            file_dir = os.path.join(petri_nets_path, filename)

            return render(request, 'upload_pn.html', {'petrinet_list': petrinets, 'target_page': target_page})

        elif "deleteButton" in request.POST:
            if "net_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)

            filename = request.POST["net_list"]
            if settings.PETRI_NET_NAME == filename:
                settings.PETRI_NET_NAME = ":notset:"

            petrinets = [f for f in listdir(petri_nets_path) if isfile(join(petri_nets_path, f))]

            petrinets.remove(filename)
            file_dir = os.path.join(petri_nets_path, filename)
            os.remove(file_dir)
            return render(request, 'upload_pn.html', {'petrinet_list': petrinets, 'target_page': target_page})

        elif "setButton" in request.POST:
            if "net_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)

            filename = request.POST["net_list"]
            settings.PETRI_NET_NAME = filename

            petrinets = [f for f in listdir(petri_nets_path) if isfile(join(petri_nets_path, f))]

            return render(request, 'upload_pn.html', {'petrinet_list': petrinets, 'net_name': filename})

        elif "downloadButton" in request.POST:
            if "net_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)

            filename = request.POST["net_list"]
            file_dir = os.path.join(petri_nets_path, filename)

            try:
                wrapper = FileWrapper(open(file_dir, 'rb'))
                response = HttpResponse(wrapper, content_type='application/force-download')
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_dir)
                return response
            except Exception:
                return None

    else:
        petrinets = [f for f in listdir(petri_nets_path) if isfile(join(petri_nets_path, f))]
        return render(request, 'upload_pn.html', {'petrinet_list': petrinets, 'target_page': target_page})
