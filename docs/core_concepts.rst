=============
Core concepts
=============

.. _`core_concepts`:

``django-lb-workflow`` is ``Activity-Based Workflow``.
Activity-based workflow systems have workflow processes comprised of activities
to be completed in order to accomplish a goal.

.. image:: _static/demo-flow.png

Half Config
-----------

``django-lb-workflow`` is ``half config``.

- ``Data model``/``action``/``Layout of form`` is written by code.
    - They are too complex to config and the change is not too often.
- The node(activity) and transition is configurable.
    - The pattern is clear and the change is often.

Data model
----------

Config
######

**Process**

A process holds the map that describes the flow of work.

The process map is made of nodes and transitions. The instances you create on the
map will begin the flow in the draft node. Instances can be moved forward from node
to node, going through transitions, until they reach the end node.

**Node**

Node is the states of an instance.

**Transition**

A Transition connects two node: a From and a To activity.

Since the transition is oriented you can think at it as being a
link starting from the From and ending in the To node.
Linking the nodes in your process you will be able to draw the map.

Each transition can have a condition that will be tested
whether this transition is available.

Each transition is associated to a app that define an action to perform.

**App**

An application is a python view that can be called by URL.

Runtime
#######

**ProcessInstance**

A process instance is created when someone decides to do something,
and doing this thing means start using a process defined in ``django-lb-workflow``.
That's why it is called "process instance". The process is a class
(=the definition of the process), and each time you want to
"do what is defined in this process", that means you want to create
an INSTANCE of this process.

So from this point of view, an instance represents your dynamic
part of a process. While the process definition contains the map
of the workflow, the instance stores your usage, your history,
your state of this process.

**Task**

A task object represents a task you are performing.

**Event**

A task perform log.

**BaseWFObj**

A abstract class for flow model. Every flow model should inherit from it.


Views and Forms
---------------

``django-lb-workflow`` provide a set of views and forms to customized flow.

url provide by ``django-lb-workflow``
#####################################

you can find all url in ``lbworkflow/urls.py``

- Main entrance
    - Todo
    - I submitted
    - Start a new flow
    - Reports
- Flow
    - New
    - Edit
    - Delete
    - List(Report)
    - Detail
    - Print
- Actions(App)
    - Agree
    - Back to
    - Reject
    - Give up
    - Batch agree
    - Batch reject
    - Batch give up
    - Execute customized transition
