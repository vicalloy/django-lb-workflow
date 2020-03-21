from django.http import HttpResponse
from django.template import Context
from django.template import Template

from lbworkflow.models import Process

try:
    import pygraphviz as pgv
except ImportError:
    pass


def generate_process_flowchart(process):
    file_template = """
        strict digraph {
            rankdir=TB;
            graph [ratio="auto"
                label="{{ name }}"
                labelloc=t
                ];
            node [shape = ellipse];
            {
                node [shape=diamond label="Router"];
                {% for node in router_nodes %}
                {{ node.name }};
                {% endfor %}
            }
            edge [fontsize=14]
            {% for transition in transitions %}
            "{{ transition.input_node.name }}" -> "{{ transition.output_node.name }}"
            [label="{{ transition.name }} {% if transition.get_condition_descn %}: {% endif %} {{ transition.get_condition_descn }}"] ;
            {% endfor %}
        }
    """  # NOQA
    transitions = process.transition_set.all()
    router_nodes = process.node_set.filter(node_type='router')
    request = Context(
        {
            'name': process.name,
            'router_nodes': router_nodes,
            'transitions': transitions
        }
    )
    t = Template(file_template)
    G = pgv.AGraph(string=t.render(request))
    return G


def render_dot_graph(graph):
    image_data = graph.draw(format='png', prog='dot')
    return HttpResponse(image_data, content_type="image/png")


def process_flowchart(request, wf_code):
    process = Process.objects.get(code=wf_code)
    G = generate_process_flowchart(process)
    return render_dot_graph(G)
