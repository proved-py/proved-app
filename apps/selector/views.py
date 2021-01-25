from django.shortcuts import render


def artifact_selector(type):
    artifact_map = {}


def selector(request):
    if request.method == 'POST':
        if 'algorithm_request' in request.method:
            pass
        elif 'upload' in request.method:
            pass
        elif 'delete' in request.method:
            pass
        else: # 'algorithm' is in request.POST, dispatch to the correct algorithm page
            return render(request, request.POST['algorithm'], )

    context = {}
    return render(request, 'selector.html', context)
