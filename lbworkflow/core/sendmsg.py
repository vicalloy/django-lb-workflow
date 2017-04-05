from lbworkflow import settings

from .helper import as_func


# wf_send_sms(users, mail_type, event, ext_ctx)
# wf_send_mail(users, mail_type, event, ext_ctx)

def wf_send_msg(users, msg_type, event=None, ext_ctx=None):
    if not users:
        return

    users = set(users)
    if event:  # ignore operator
        if event.user in users:
            users = users.remove(event.user)

    for send_msg in settings.WF_SEND_MSG_FUNCS:
        as_func(send_msg)(users, msg_type, event, ext_ctx)


def wf_print(users, msg_type, event=None, ext_ctx=None):
    print("wf_print: %s, %s, %s" % (users, msg_type, event))
