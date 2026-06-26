from django.shortcuts import redirect, render

from apps.dashboard.services.summary import get_dashboard_summary
from apps.security.decorators import app_access_required


@app_access_required
def home(request):
    summary = get_dashboard_summary(request.user)
    return render(
        request,
        "dashboard/home.html",
        {
            "summary": summary,
        },
    )


def access_denied(request):
    if not request.user.is_authenticated:
        return redirect("security:login")

    profile = request.user.profile
    if not profile.is_security_complete:
        return redirect("security:login")

    return render(request, "dashboard/access_denied.html")
