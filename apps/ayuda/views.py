from django.shortcuts import render

from apps.security.decorators import app_access_required


@app_access_required
def ayuda_home(request):
    return render(request, "ayuda/home.html")
