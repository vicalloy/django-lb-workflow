import inspect
import os
import shutil
import stat

from jinja2 import Environment
from jinja2 import FileSystemLoader

__all__ = (
    'FlowAppGenerator', 'clean_generated_files'
)


def clean_generated_files(model_class):
    folder_path = os.path.dirname(inspect.getfile(model_class))
    for path, dirs, files in os.walk(folder_path):
        if not path.endswith(model_class.__name__.lower()):
            shutil.rmtree(path)
        for file in files:
            if file not in ['models.py', 'wfdata.py', '__init__.py']:
                try:
                    os.remove(os.path.join(path, file))
                except:  # NOQA
                    pass


def get_fields(model_class):
    fields = []
    ignore_fields = ['id', 'pinstance', 'created_on', 'created_by']
    for f in model_class._meta.fields:
        if f.name not in ignore_fields:
            fields.append(f)
    return fields


def get_field_names(model_class):
    fields = get_fields(model_class)
    return ', '.join(["'%s'" % e.name for e in fields])


def group(flat_list):
    for i in range(len(flat_list) % 2):
        flat_list.append(None)
        pass
    return list(zip(flat_list[0::2], flat_list[1::2]))


class FlowAppGenerator(object):
    def __init__(self, app_template_path=None):
        if not app_template_path:
            app_template_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'app_template')
        self.app_template_path = app_template_path
        super().__init__()

    def init_env(self, template_path):
        loader = FileSystemLoader(template_path)
        self.env = Environment(
            block_start_string='[%',
            block_end_string='%]',
            variable_start_string='[[',
            variable_end_string=']]',
            comment_start_string='[#',
            comment_end_string='#]',
            loader=loader,
        )

    def gen(self, model_class, item_model_class_list=None, wf_code=None, replace=False, ignores=['wfdata.py']):
        dest = os.path.dirname(inspect.getfile(model_class))
        app_name = model_class.__module__.split('.')[-2]
        if not wf_code:
            wf_code = app_name
        ctx = {
            'app_name': app_name,
            'wf_code': wf_code,
            'class_name': model_class.__name__,
            'wf_name': model_class._meta.verbose_name,
            'field_names': get_field_names(model_class),
            'fields': get_fields(model_class),
            'grouped_fields': group(get_fields(model_class)),
        }
        if item_model_class_list:
            item_list = []
            for item_model_class in item_model_class_list:
                item_ctx = {
                    'class_name': item_model_class.__name__,
                    'lowercase_class_name': item_model_class.__name__.lower(),
                    'field_names': get_field_names(item_model_class),
                    'fields': get_fields(item_model_class),
                    'grouped__fields': group(get_fields(item_model_class)),
                }
                item_list.append(item_ctx)
            ctx['item_list'] = item_list
        self.copy_template(self.app_template_path, dest, ctx, replace, ignores)

    def copy_template(self, src, dest, ctx={}, replace=False, ignores=[]):
        self.init_env(src)
        for path, dirs, files in os.walk(src):
            relative_path = path[len(src):].lstrip(os.path.sep)
            dest_path = os.path.join(dest, relative_path)
            dest_path = dest_path.replace('app_name', ctx.get('app_name', 'app_name'))
            if not os.path.exists(dest_path):
                os.mkdir(dest_path)
            for i, subdir in enumerate(dirs):
                if subdir.startswith('.'):
                    del dirs[i]
            for filename in files:
                if filename.endswith('.pyc') or filename.startswith('.'):
                    continue
                src_file_path = os.path.join(path, filename)
                src_file_path = src_file_path[len(src):].strip(os.path.sep)
                dest_file_path = os.path.join(dest, relative_path, filename)
                dest_file_path = dest_file_path.replace('app_name', ctx.get('app_name', 'app_name'))
                if dest_file_path.endswith('-tpl'):
                    dest_file_path = dest_file_path[:-4]

                is_exists = os.path.isfile(dest_file_path)
                for ignore in ignores:
                    if dest_file_path.endswith(ignore):
                        replace = False
                if is_exists and not replace:
                    continue
                self.copy_template_file(src_file_path, dest_file_path, ctx)

    def copy_template_file(self, src, dest, ctx={}):
        if os.path.sep != '/':
            # https://github.com/pallets/jinja/issues/767
            # Jinja template names are not fileystem paths.
            # They always use forward slashes so this is working as intended.
            src = src.replace(os.path.sep, '/')
        template = self.env.get_template(src)
        template.stream(ctx).dump(dest, encoding='utf-8')
        # Make new file writable.
        if os.access(dest, os.W_OK):
            st = os.stat(dest)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(dest, new_permissions)
