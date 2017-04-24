from lbworkflow.core.datahelper import create_app


def load_data():
    load_base()


def load_base():
    create_app('5f31d065-00aa-0010-beea-641f0a670010', 'Simple', action='wf_execute_transition')
    create_app('5f31d065-00aa-0010-beea-641f0a670020', 'Customized URL')
