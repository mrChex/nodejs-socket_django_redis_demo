# -*- coding: utf-8 -*-
import redis

from django.views.generic import View
from app.utils import render_to


class Index(View):

    @render_to('main/index.html')
    def get(self, request):
        if not 'randomint' in request.session:
            import random
            request.session['randomint'] = random.randrange(0, 10)
        return {"randomint": request.session['randomint']}

    @render_to('json')
    def post(self, request):
        redis_pub = redis.Redis(db=0)
        redis_pub.publish("nodejs", {"randomint": request.session['randomint'],
                                     "sended_via": "redis"})

        return {"randomint": request.session['randomint']}