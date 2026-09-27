def user_roles(request):
    user = getattr(request, 'user', None)
    is_editor = False
    if user and user.is_authenticated:
        is_editor = (
            user.groups.filter(name__iexact='Editor').exists()
            or user.has_perm('main.change_experience')
            or user.has_perm('main.change_project')
        )
    return {
        'is_editor': is_editor,
    }
