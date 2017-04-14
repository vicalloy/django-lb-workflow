from django.utils.deprecation import MiddlewareMixin
from stronghold.middleware import LoginRequiredMiddleware


class LoginRequiredStrongholdMiddleware(MiddlewareMixin, LoginRequiredMiddleware):
    pass