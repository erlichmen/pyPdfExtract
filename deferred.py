from google.appengine.ext import deferred
from google.appengine.ext.deferred import SingularTaskFailure
import simple_ioc as ioc

_DEFAULT_URL = "/_ah/queue/deferred"


def set_defer_method(defer_method):
    ioc.features.Provide('DeferredMethod', defer_method)


def get_defer_method():
    return ioc.RequiredFeature('DeferredMethod', default=deferred.defer).result


def do_defer(method, *args, **kwargs):
    deferred_method = get_defer_method()

    tag = kwargs.pop("_tag") if kwargs.get('_tag') else None

    if not tag and kwargs.get('_queue'):
        tag = kwargs.get('_queue')

    # kwargs['_url'] = '%s/%s' % (_DEFAULT_URL, tag or 'notag')
    kwargs['_url'] = '%s/%s/%s' % (_DEFAULT_URL, method.__name__, tag or 'notag')

    deferred_method(method, *args, **kwargs)


__all__ = ['SingularTaskFailure', 'set_defer_method', 'get_defer_method', 'do_defer']
