from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token


@requires_csrf_token
def page_not_found(request, exception):
    """Обработчик ошибки 404"""
    return render(request, 'pages/404.html', status=404)


@requires_csrf_token
def server_error(request):
    """Обработчик ошибки 500"""
    return render(request, 'pages/500.html', status=500)


@requires_csrf_token
def csrf_failure(request, reason=''):
    """Обработчик ошибки 403"""
    return render(request, 'pages/403csrf.html', status=403)
