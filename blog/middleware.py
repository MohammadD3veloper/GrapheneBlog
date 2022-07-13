from .models import WebsiteView
from django.db import IntegrityError



class WebsiteViewsMiddleware(object):
    def resolve(self, next, root, info, **args):
        ip_address = info.context.META.get('HTTP_X_FORWARDED_FOR')
        user_agent = info.context.META.get('HTTP_USER_AGENT')
        if not ip_address:
            ip_address = info.context.META['REMOTE_ADDR']
            if not ip_address:
                ip_address = '127.0.0.1'
            try:
                WebsiteView.objects.create(
                    user_ip=ip_address,
                    user_agent=user_agent
                )
            except IntegrityError:
                pass
        return next(root, info, **args)