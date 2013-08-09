# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.template import RequestContext, loader


def render_to(template=None):
    def renderer(function):
        def wrapper(self, request, *args, **kwargs):
            output = function(self, request, *args, **kwargs)

            if 'redirect' in output:
                return HttpResponseRedirect(output['redirect'])

            if template == "json":
                json_string = json.dumps(output)
                return HttpResponse(json_string)
            else:
                t = loader.get_template(template)

                output['request'] = request
                return HttpResponse(t.render(RequestContext(request, output)))

        return wrapper
    return renderer