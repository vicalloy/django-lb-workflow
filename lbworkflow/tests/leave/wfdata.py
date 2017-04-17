from lbworkflow.core.datahelper import create_activity
from lbworkflow.core.datahelper import create_app
from lbworkflow.core.datahelper import create_category
from lbworkflow.core.datahelper import create_process
from lbworkflow.core.datahelper import create_transition


def load_data(wf_code):
    create_app('5f31d065-00aa-0010-beea-641f0a670010', 'Simple URL', action='wf_execute_transition')
    category = create_category('5f31d065-00cc-0010-beea-641f0a670010', 'HR')

    process = create_process('leave', 'Leave', category=category)
    create_activity('5f31d065-00a0-0010-beea-641f0a670010', process, 'Draft', status='draft')
    create_activity('5f31d065-00a0-0010-beea-641f0a670020', process, 'Given up', status='given up')
    create_activity('5f31d065-00a0-0010-beea-641f0a670030', process, 'Rejected', status='rejected')
    create_activity('5f31d065-00a0-0010-beea-641f0a670040', process, 'Completed', status='completed')
    create_activity('5f31d065-00a0-0010-beea-641f0a670050', process, 'A1', operators='[owner]')
    create_activity('5f31d065-00a0-0010-beea-641f0a670060', process, 'A2', operators='[tom]')
    create_activity('5f31d065-00a0-0010-beea-641f0a670070', process, 'A3', operators='[vicalloy]')
    create_transition('5f31d065-00e0-0010-beea-641f0a670010', process, 'Draft,', 'A1')
    create_transition('5f31d065-00e0-0010-beea-641f0a670020', process, 'A1,', 'A2')
    create_transition('5f31d065-00e0-0010-beea-641f0a670030', process, 'A2,', 'A3')
    create_transition('5f31d065-00e0-0010-beea-641f0a670040', process, 'A3,', 'Completed')
