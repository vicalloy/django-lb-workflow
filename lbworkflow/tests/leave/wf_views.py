from lbworkflow.views.transition import ExecuteTransitionView

from .forms import HRForm


class CustomizedTransitionView(ExecuteTransitionView):
    form_classes = {
        'form': HRForm
    }


c = CustomizedTransitionView.as_view()
