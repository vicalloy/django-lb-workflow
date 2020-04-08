from lbworkflow.version import get_version

VERSION = (0, 9, 9, 'alpha', 0)

__version__ = get_version(VERSION)

default_app_config = 'lbworkflow.apps.LBWorkflowConfig'
