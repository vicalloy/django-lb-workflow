from django import template

register = template.Library()


@register.filter
def app_url(transition, task):
    return transition.get_app_url(task)


@register.filter
def flow_status_css_class(pinstance):
    if not pinstance:
        return "default"
    if pinstance.cur_node.status in ["rejected"]:
        return "danger"
    if pinstance.cur_node.status == "in progress":
        return "info"
    if pinstance.cur_node.status == "finished":
        return "success"
    return "default"


@register.filter
def category_have_perm_processes(category, user):
    return category.get_can_apply_processes(user)


@register.filter(is_safe=True)
def mermaid_transition_line(transition, event_transitions):
    if (transition.input_node, transition.output_node) in event_transitions:
        return "-->"
    return "-.->"
