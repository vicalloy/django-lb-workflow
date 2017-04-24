from lbworkflow.core.datahelper import create_user


def load_data():
    init_users()


def init_users():
    users = {
        'owner': create_user('owner'),
        'operator': create_user('operator'),
        'vicalloy': create_user('vicalloy'),
        'tom': create_user('tom'),
        'hr': create_user('hr'),
        'admin': create_user('admin', is_superuser=True, is_staff=True),
    }
    return users
