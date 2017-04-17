from lbworkflow.models import Activity
from lbworkflow.models import Transition
from lbworkflow.models import App
from lbworkflow.models import Process


def get_or_create(cls, uid, **kwargs):
    uid_field_name = kwargs.pop('uid_field_name', 'uuid')
    obj = cls.objects.filter(**{uid_field_name: uid}).first()
    if obj:
        return obj
    kwargs[uid_field_name] = uid
    return cls.objects.create(**kwargs)


def create_app(uuid, name, **kwargs):
    return get_or_create(App, uuid, name=name, **kwargs)


def create_process(code, name, **kwargs):
    return get_or_create(Process, code, name=name, uid_field_name='code', **kwargs)


def create_activity(uuid, process, name, **kwargs):
    return get_or_create(Activity, uuid, process=process, name=name, **kwargs)


def get_activity(process, name):
    """
    get activity
    :param process: 
    :param name: 'submit' or 'submit,5f31d065-4a87-487b-beea-641f0a6720c3' 
    :return: activity
    """
    name_and_uuid = [e.strip() for e in name.split(',') if e.strip()]
    qs = Activity.objects.filter(process=process)
    if len(name_and_uuid) == 1:
        qs = qs.filter(name=name_and_uuid[0])
    else:
        qs = qs.filter(uuid=name_and_uuid[1])
    return qs[0]


def create_transition(uuid, process, from_activity, to_activity, app=None, **kwargs):
    from_activity = get_activity(process, from_activity)
    to_activity = get_activity(process, to_activity)
    if not app:
        app = App.objects.get(name='Simple URL')
    return get_or_create(
        Transition, uuid, process=process, input_activity=from_activity,
        output_activity=to_activity, app=app, **kwargs)