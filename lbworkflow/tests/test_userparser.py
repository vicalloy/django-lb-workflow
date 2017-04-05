from django.contrib.auth import get_user_model

from lbworkflow.core.userparser import SimpleUserParser

from .test_base import BaseTests

User = get_user_model()


class UserSimpleParserTests(BaseTests):

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
        users = SimpleUserParser('[o.created_by]', self.leave.pinstance).parse()
        self.assertEqual(users[0], self.users['owner'])

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
