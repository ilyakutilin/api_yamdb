from rest_framework import permissions


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            # TODO: ILYA
            # Чтобы было удобно работать с ролями пользователя,
            # необходимо реализовать в модели User свойства,
            # который будут выполнять данные проверки.
            # Например:
            # @property
            # def is_<роль_пользователя>(self):
            #     return self.role == User.<роль_пользователя>
            # Далее в любом месте работая с объектом модели User можно будет
            # выполнить проверку вызовом данного свойства.
            or (request.user.role in ('moderator', 'admin')
                or request.user.is_staff)
        )


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            # TODO: ILYA
            # См. замечания про проверку роли пользователя.
            and (request.user.role == 'admin' or request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.role == 'admin'
            or request.user.is_staff
        )
