from django.shortcuts import render

APP_BASE_DIR = 'dashboard/'
APP_TEMPLATES_DIR = APP_BASE_DIR + 'templates/'


def dashboard(request):
    context = {'hello_world': 'Hello, world!'}
    return render(request, APP_TEMPLATES_DIR + 'dashboard.html', context)
