from django.shortcuts import render

from django.shortcuts import render


def explorer(request):
    context = {}
    return render(request, 'explorer.html', context)
