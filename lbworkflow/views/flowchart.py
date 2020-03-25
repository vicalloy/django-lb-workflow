from django.template import Context
from django.template import Template

from lbworkflow.models import Process
from lbworkflow.models import ProcessInstance


def get_event_transitions(process_instance):
    from lbworkflow.models import Event
    events = Event.objects.filter(instance=process_instance).order_by('-created_on', '-id')
    transitions = []
    for event in events:
        transition = (event.old_node, event.new_node)
        if event.new_node.status not in ['in progress']:
            transitions.append(transition)
            break
        if transition not in transitions:
            transitions.append(transition)
    return transitions


def generate_mermaid_src(process_instance):
    file_template = """
    {% load lbworkflow_tags %}
    graph TD
    {% for node in nodes %}
    {% if node.node_type == 'router' %}
    {{node.pk}}{ {{node.name}} }
    {% else %}
    {{node.pk}}( {{node.name}} )
    {% endif %}
    {% endfor %}
    {% for transition in transitions %}
    {{ transition.input_node.pk }} {{ transition|mermaid_transition_line:event_transitions|safe }}{% if transition.get_condition_descn %}|{{transition.get_condition_descn}}|{% endif %} {{ transition.output_node.pk }}
    {% endfor %}
    """  # NOQA
    if isinstance(process_instance, Process):
        process = process_instance
        process_instance = None
    else:
        process = process_instance.process

    transitions = process.transition_set.all()
    event_transitions = []
    if process_instance:
        event_transitions = get_event_transitions(process_instance)

    nodes = process.node_set.all()
    ctx = Context(
        {
            'name': process.name,
            'nodes': nodes,
            'transitions': transitions,
            'event_transitions': event_transitions
        }
    )
    t = Template(file_template)
    return t.render(ctx)


def process_flowchart(request, wf_code):
    from django.shortcuts import render
    template_name = 'lbworkflow/flowchart.html'
    process = Process.objects.get(code=wf_code)
    graph_src = generate_mermaid_src(process)
    ctx = {
        'process': process,
        'graph_src': graph_src
    }
    return render(request, template_name, ctx)


def process_instance_flowchart(request, pk):
    from django.shortcuts import render
    template_name = 'lbworkflow/flowchart.html'
    process_instance = ProcessInstance.objects.get(pk=pk)
    graph_src = generate_mermaid_src(process_instance)
    ctx = {
        'process': process_instance.process,
        'graph_src': graph_src
    }
    return render(request, template_name, ctx)
