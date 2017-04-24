from django.contrib.auth import get_user_model
from lbutils import as_callable

from lbworkflow.models import Activity
from lbworkflow.models import App
from lbworkflow.models import Process
from lbworkflow.models import ProcessCategory
from lbworkflow.models import Transition

User = get_user_model()


def get_or_create(cls, uid, **kwargs):
    uid_field_name = kwargs.pop('uid_field_name', 'uuid')
    obj = cls.objects.filter(**{uid_field_name: uid}).first()
    if obj:
        for k, v in kwargs.items():
            setattr(obj, k, v)
        obj.save()
        return obj
    kwargs[uid_field_name] = uid
    return cls.objects.create(**kwargs)


def create_user(username, **kwargs):
    password = kwargs.pop('password', 'password')
    user = User.objects.filter(username=username).first()
    if user:
        user.set_password(password)
        return user
    return User.objects.create_user(username, "%s@v.cn" % username, password, **kwargs)


def create_app(uuid, name, **kwargs):
    return get_or_create(App, uuid, name=name, **kwargs)


def create_category(uuid, name, **kwargs):
    return get_or_create(ProcessCategory, uuid, name=name, **kwargs)


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


def get_app(name):
    """
    get activity
    :param process:
    :param name: 'submit' or 'submit,5f31d065-4a87-487b-beea-641f0a6720c3'
    :return: activity
    """
    name_and_uuid = [e.strip() for e in name.split(',') if e.strip()]
    qs = App.objects
    if len(name_and_uuid) == 1:
        qs = qs.filter(name=name_and_uuid[0])
    else:
        qs = qs.filter(uuid=name_and_uuid[1])
    return qs[0]


def create_transition(uuid, process, from_activity, to_activity, app='Simple', **kwargs):
    from_activity = get_activity(process, from_activity)
    to_activity = get_activity(process, to_activity)
    app = get_app(app)
    return get_or_create(
        Transition, uuid, process=process, input_activity=from_activity,
        output_activity=to_activity, app=app, **kwargs)


def load_wf_data(app, wf_code=''):
    if wf_code:
        func = "%s.wfdata.load_%s" % (app, wf_code)
    else:
        func = "%s.wfdata.load_data" % app
    as_callable(func)()
