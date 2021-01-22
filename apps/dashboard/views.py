from django.shortcuts import render


def dashboard(request):
    context = {'hello_world': 'Hello, world!'}
    return render(request, 'dashboard.html', context)
