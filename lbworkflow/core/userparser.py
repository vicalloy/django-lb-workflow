from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from lbutils import get_or_none

from lbworkflow.core.helper import safe_eval

User = get_user_model()


def remove_brackets(s, start_char="[", end_char="]"):
    return s.strip(start_char).strip(end_char).strip()


class BaseUserParser(object):

    def __init__(self, param, pinstance=None, operator=None, owner=None):
        self.owner = owner
        self.operator = operator
        self.param = param
        self.pinstance = pinstance
        self.wf_obj = None
        if pinstance:
            self.wf_obj = pinstance.content_object
            self.owner = pinstance.created_by

    def _get_eval_val(self, eval_str):
        return safe_eval(eval_str, {'o': self.wf_obj})

    def eval_as_list(self, eval_str):
        v = self._get_eval_val(eval_str)
        if v.__class__.__name__ == 'ManyRelatedManager':
            return v.all()
        if isinstance(v, models.Model):
            return [v]
        return v

    def parse(self):
        return []


class SimpleUserParser(BaseUserParser):
    def process_func(self, func_str):
        return None

    def _get_users(self, user_str):
        """
        #owner
        #operator
        [11:vicalloy]
        [o.auditor]
        [o.auditors]
        """
        user_str = remove_brackets(user_str)
        if user_str.startswith('#'):
            user_str = user_str[1:]
            if user_str == 'owner':
                return [self.owner]
            elif user_str == 'operator':
                return [self.operator]
        if '.' in user_str:
            return self.eval_as_list(user_str)
        if ':' in user_str:
            pk = user_str.split(':')[0]
            return User.objects.filter(pk=pk)
        return User.objects.filter(username=user_str)

    def _get_groups(self, group_str):
        """
        g[o.group]
        g[o.groups]
        g[11:admins]
        """
        group_str = remove_brackets(group_str, 'g[')
        if '.' in group_str:
            return self.eval_as_list(group_str)
        pk = group_str.split(':')[0]
        group = get_or_none(Group, pk=pk)
        return [group] if group else []

    def _get_users_by_groups(self, group_str):
        groups = self._get_groups(group_str)
        return User.objects.filter(group__in=groups)

    def _paser_atom_rule(self, atom_rule):
        """
        #owner
        #operator
        user [11:vicalloy]
        group g[11:group]

        if syntax error will return None
        """
        if not atom_rule:
            return []
        users = self.process_func(atom_rule)
        if users is not None:  # is function
            return users
        if atom_rule.startswith('#'):
            return self._get_users(atom_rule)
        elif atom_rule.startswith('g['):  # role(group)
            return self._get_users_by_groups(atom_rule)
        elif atom_rule.startswith('['):  # user
            return self._get_users(atom_rule)
        # log it?
        return None

    def _to_users(self, rules):
        all_users = []
        for rule in rules:
            users = self._paser_atom_rule(rule)
            if users is not None:
                all_users.extend(users)
        # TODO ignore quited users
        return all_users

    def _get_active_rules(self):
        """
        :o.leave_days<7
        [vicalloy]
        :o.leave_days>=7
        [tom]
        """
        rules = [e.strip() for e in self.param.splitlines() if e.strip()]
        str_rules = ''
        need_add = True
        for rule in rules:
            is_condition = rule.startswith(':')
            if not is_condition and not need_add:
                continue
            if is_condition:
                need_add = safe_eval(rule[1:], {'o': self.wf_obj})
                continue
            str_rules = '%s,%s' % (str_rules, rule)
        return [e.strip() for e in str_rules.split(',') if e.strip()]

    def parse(self):
        rules = self._get_active_rules()
        active_rules = []
        for rule in rules:
            active_rules.append(rule)
        users = self._to_users(active_rules)
        return list(set(users))
