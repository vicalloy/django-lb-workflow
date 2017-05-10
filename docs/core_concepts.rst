=============
Core concepts
=============

.. _`core_concepts`:

``django-lb-workflow`` is ``Entity-Based Workflow``.
For example, the publication of documents on a web site can be simply modeled by
the document going through the states of new, submitted, and then approved or rejected.
In entity-based workflows, the document is the main issue and its available actions are
defined by its current status.

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
