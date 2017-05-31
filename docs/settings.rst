Settings
========

The following settings are available for configuration through your project.

All available settings can find in ``lbworkflow.settings``

List of available settings
--------------------------

LBWF_APPS
~~~~~~~~~
Default: ``{}``

Specifies the APP of process.

    >>> {'leave': 'lbworkflow.tests.leave'}.

``leave`` is the wf_code of the process.
``lbworkflow.tests.leave`` is the app of the process.


LBWF_USER_PARSER
~~~~~~~~~~~~~~~~
Default: ``lbworkflow.core.userparser.SimpleUserParser``

``django-lb-workflow`` use a text field to config users for ``Node``
and user a parser to cover it to Django model. You can replace it with your implement.
The parse must a subclass of ``lbworkflow.core.userparser.BaseUserParser``


LBWF_EVAL_FUNCS
~~~~~~~~~~~~~~~

Default: ``{}``

A list of functions that can used in ``Transition.condition``.

    >>> {'get_dept': 'hr.models.get_dept'}.

``get_detp`` can used in ``Transition.condition``.


LBWF_WF_SEND_MSG_FUNCS
~~~~~~~~~~~~~~~~~~~~~~

Default: ``['lbworkflow.core.sendmsg.wf_print', ]``

A list of functions that used to send message when process node changed.

The function must define as ``def wf_print(users, msg_type, event=None, ext_ctx=None)``
  users: A list of user need send message to.
  msg_type: The type of message. Can be ``notify/transfered/new_task``.


LBWF_GET_USER_DISPLAY_NAME_FUNC
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``lambda user: "%s" % user``

A function used to get the display name of a user.
