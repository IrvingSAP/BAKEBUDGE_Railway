def app_layout(request):
    profile = None
    is_master = False
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        if profile is not None:
            is_master = profile.is_master
    return {
        "app_profile": profile,
        "app_is_master": is_master,
    }
