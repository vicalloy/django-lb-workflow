from lbworkflow.views.transition import ExecuteTransitionView


class CustomizedTransitionView(ExecuteTransitionView):
    pass


c = CustomizedTransitionView.as_view()
