from django.test import TestCase
from django.contrib.auth import get_user_model

from lbworkflow.core.userparser import SimpleUserParser


User = get_user_model()


class UserSimpleParserTests(TestCase):

    def setUp(self):
        def create_user(username):
            return User.objects.create(username=username, password='pass')
        super(UserSimpleParserTests, self).setUp()
        self.users = {
            'owner': create_user('owner'),
            'operator': create_user('operator'),
            'vicalloy': create_user('vicalloy'),
        }

    def test_parser_users(self):
        users = SimpleUserParser('[vicalloy]').parse()
        self.assertEqual(users[0], self.users['vicalloy'])

        users = SimpleUserParser(
            '[%s:vicalloy]' % self.users['vicalloy'].pk
        ).parse()
        self.assertEqual(users[0], self.users['vicalloy'])

        users = SimpleUserParser('#owner', owner=self.users['owner']).parse()
        self.assertEqual(users[0], self.users['owner'])

        users = SimpleUserParser(
            '#operator', operator=self.users['operator']
        ).parse()
        self.assertEqual(users[0], self.users['operator'])

    def test_eval_as_list(self):
        # [o.auditors]
        # TODO
        pass

    def test_condition_rules(self):
        rules = """
        :True
        [owner]
        [operator]
        :False
        [vicalloy]
        """
        users = SimpleUserParser(
            rules,
            operator=self.users['operator'],
            owner=self.users['owner'],
        ).parse()
        self.assertEqual(
            set(users), set([self.users['owner'], self.users['operator']])
        )

    def test_parser_groups(self):
        # TODO
        pass
