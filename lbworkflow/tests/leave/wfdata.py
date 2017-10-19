from lbworkflow.core.datahelper import create_category
from lbworkflow.core.datahelper import create_node
from lbworkflow.core.datahelper import create_process
from lbworkflow.core.datahelper import create_transition


def load_data():
    load_leave()


def load_leave():
    """ load_[wf_code] """
    category = create_category('5f31d065-00cc-0010-beea-641f0a670010', 'HR')
    process = create_process('leave', 'Leave', category=category)
    create_node('5f31d065-00a0-0010-beea-641f0a670010', process, 'Draft', status='draft')
    create_node('5f31d065-00a0-0010-beea-641f0a670010', process, 'Draft', status='draft')  # test for update
    create_node('5f31d065-00a0-0010-beea-641f0a670020', process, 'Given up', status='given up')
    create_node('5f31d065-00a0-0010-beea-641f0a670030', process, 'Rejected', status='rejected')
    create_node('5f31d065-00a0-0010-beea-641f0a670040', process, 'Completed', status='completed')
    create_node('5f31d065-00a0-0010-beea-641f0a670050', process, 'A1', operators='[owner]')
    create_node('5f31d065-00a0-0010-beea-641f0a670060', process, 'A2', operators='[tom]')
    create_node('5f31d065-00a0-0010-beea-641f0a670065', process, 'A2B1', operators='[tom],[owner]')
    create_node('5f31d065-00a0-0010-beea-641f0a670070', process, 'A3', operators='[vicalloy]')
    create_node('5f31d065-00a0-0010-beea-641f0a670080', process, 'A4', operators='[hr]')
    create_node('5f31d065-00a0-0010-beea-641f0a670a10', process, 'R1', operators='', node_type='router')
    create_transition('5f31d065-00e0-0010-beea-641f0a670010', process, 'Draft,', 'A1')
    create_transition('5f31d065-00e0-0010-beea-641f0a670020', process, 'A1,', 'A2')
    create_transition(
        '5f31d065-00e0-0010-beea-641f0a670030', process, 'A2,', 'A3',
        condition='o.leave_days<7  # days<7')
    create_transition(
        '5f31d065-00e0-0010-beea-641f0a670040', process, 'A2,', 'A2B1',
        condition='o.leave_days>=7  # days>=7')
    create_transition(
        '5f31d065-00e0-0010-beea-641f0a670050', process, 'A2B1,', 'A3',
        routing_rule='joint', can_auto_agree=False)
    create_transition('5f31d065-00e0-0010-beea-641f0a670060', process, 'A3,', 'A4')
    create_transition(
        '5f31d065-00e0-0010-beea-641f0a670070', process, 'A4,', 'R1',
        app='Customized URL', app_param='wf_execute_transition {{wf_code}} c')
    create_transition('5f31d065-00e0-0010-beea-641f0a670080', process, 'R1,', 'Completed')
