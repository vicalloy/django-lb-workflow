from lbworkflow.core.datahelper import create_category
from lbworkflow.core.datahelper import create_node
from lbworkflow.core.datahelper import create_process
from lbworkflow.core.datahelper import create_transition


def load_data():
    load_simplewf()


def load_simplewf():
    category = create_category('5f31d065-00cc-0020-beea-641f0a670010', 'HR')

    process = create_process('simplewf__A', 'Simple Workflow: A', category=category)
    create_node('5f31d666-00a0-0020-beea-641f0a670010', process, 'Draft', status='draft')
    create_node('5f31d666-00a0-0020-beea-641f0a670020', process, 'Given up', status='given up')
    create_node('5f31d666-00a0-0020-beea-641f0a670030', process, 'Rejected', status='rejected')
    create_node('5f31d666-00a0-0020-beea-641f0a670040', process, 'Completed', status='completed')
    create_node('5f31d666-00a0-0020-beea-641f0a670050', process, 'A1', operators='[owner]')
    create_transition('5f31d666-00e0-0020-beea-641f0a670010', process, 'Draft,', 'A1')
    create_transition('5f31d666-00e0-0020-beea-641f0a670020', process, 'A1,', 'Completed')

    process = create_process('simplewf__B', 'Simple Workflow: B', category=category)
    create_node('5f31d667-00a0-0020-beea-641f0a670010', process, 'Draft', status='draft')
    create_node('5f31d667-00a0-0020-beea-641f0a670020', process, 'Given up', status='given up')
    create_node('5f31d667-00a0-0020-beea-641f0a670030', process, 'Rejected', status='rejected')
    create_node('5f31d667-00a0-0020-beea-641f0a670040', process, 'Completed', status='completed')
    create_node('5f31d667-00a0-0020-beea-641f0a670050', process, 'A1', operators='[owner]')
    create_transition('5f31d667-00e0-0020-beea-641f0a670010', process, 'Draft,', 'A1')
    create_transition('5f31d667-00e0-0020-beea-641f0a670020', process, 'A1,', 'Completed')
