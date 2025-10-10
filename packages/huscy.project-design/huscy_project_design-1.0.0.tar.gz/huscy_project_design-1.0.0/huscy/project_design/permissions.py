from rest_framework.permissions import BasePermission

from huscy.projects.services import is_project_member, is_project_member_with_write_permission


class ViewProjectPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return any([
                request.user.has_perm('projects.view_project'),
                is_project_member(view.project, request.user),
            ])
        return True

    def has_object_permission(self, request, view, instance):
        return self.has_permission(request, view)


class ChangeProjectPermission(BasePermission):
    def has_change_permission(self, project, user):
        return any([
            user.has_perm('projects.change_project'),
            is_project_member_with_write_permission(project, user),
        ])

    def has_permission(self, request, view):
        if request.method in ['POST']:
            return self.has_change_permission(view.project, request.user)
        return True

    def has_object_permission(self, request, view, instance):
        if request.method in ['DELETE', 'PATCH', 'PUT']:
            return self.has_change_permission(view.project, request.user)
        return True
