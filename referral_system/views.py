from django.shortcuts import render


def index(request):
    """Главная страница с интерфейсом для тестирования"""
    return render(request, 'index.html')


def api_docs(request):
    """Страница с документацией API"""
    return render(request, 'api_docs.html')
