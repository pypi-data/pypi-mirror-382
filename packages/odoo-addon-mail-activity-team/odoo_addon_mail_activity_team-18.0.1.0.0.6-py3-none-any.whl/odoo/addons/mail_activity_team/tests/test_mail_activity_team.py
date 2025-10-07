# Copyright 2018-22 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
from datetime import date

from odoo.exceptions import ValidationError
from odoo.modules.migration import load_script
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMailActivityTeam(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Start from a clean slate
        cls.env["mail.activity.team"].search([]).unlink()
        # Create Users
        cls.employee = cls.env["res.users"].create(
            {
                "company_id": cls.env.ref("base.main_company").id,
                "name": "Employee",
                "login": "csu",
                "email": "crmuser@yourcompany.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                        ],
                    )
                ],
            }
        )
        cls.employee2 = cls.env["res.users"].create(
            {
                "company_id": cls.env.ref("base.main_company").id,
                "name": "Employee 2",
                "login": "csu2",
                "email": "crmuser2@yourcompany.com",
                "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
            }
        )
        cls.employee3 = cls.env["res.users"].create(
            {
                "company_id": cls.env.ref("base.main_company").id,
                "name": "Employee 3",
                "login": "csu3",
                "email": "crmuser3@yourcompany.com",
                "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
            }
        )
        # Create Activity Types
        cls.activity1 = cls.env["mail.activity.type"].create(
            {
                "name": "Initial Contact",
                "delay_count": 5,
                "delay_unit": "days",
                "summary": "ACT 1 : Presentation, barbecue, ... ",
                "res_model": "res.partner",
            }
        )
        cls.activity2 = cls.env["mail.activity.type"].create(
            {
                "name": "Call for Demo",
                "delay_count": 6,
                "delay_unit": "days",
                "summary": "ACT 2 : I want to show you my ERP !",
                "res_model": "res.partner",
            }
        )
        # Create Teams and Activities
        cls.partner_client = cls.env.ref("base.res_partner_1")
        cls.partner_ir_model = cls.env["ir.model"]._get("res.partner")
        cls.act1 = (
            cls.env["mail.activity"]
            .with_user(cls.employee)
            .create(
                {
                    "activity_type_id": cls.activity1.id,
                    "note": "Partner activity 1.",
                    "res_id": cls.partner_client.id,
                    "res_model_id": cls.partner_ir_model.id,
                    "user_id": cls.employee.id,
                }
            )
        )
        cls.team1 = cls.env["mail.activity.team"].create(
            {
                "name": "Team 1",
                "res_model_ids": [(6, 0, [cls.partner_ir_model.id])],
                "member_ids": [(6, 0, [cls.employee.id])],
            }
        )
        cls.team2 = cls.env["mail.activity.team"].create(
            {
                "name": "Team 2",
                "res_model_ids": [(6, 0, [cls.partner_ir_model.id])],
                "member_ids": [(6, 0, [cls.employee.id, cls.employee2.id])],
            }
        )
        cls.act2 = (
            cls.env["mail.activity"]
            .with_user(cls.employee)
            .sudo()
            .create(
                {
                    "activity_type_id": cls.activity2.id,
                    "note": "Partner activity 2.",
                    "res_id": cls.partner_client.id,
                    "res_model_id": cls.partner_ir_model.id,
                    "user_id": cls.employee.id,
                }
            )
        )

    def test_activity_members(self):
        self.team1.member_ids |= self.employee2
        self.partner_client.invalidate_recordset()
        self.assertIn(self.employee2, self.partner_client.activity_team_user_ids)
        self.assertIn(self.employee, self.partner_client.activity_team_user_ids)
        self.assertEqual(
            self.partner_client,
            self.env["res.partner"].search(
                [("activity_team_user_ids", "=", self.employee.id)]
            ),
        )

    def test_team_and_user_onchange(self):
        with self.assertRaises(ValidationError):
            self.team1.member_ids = [(3, self.employee.id)]
            self.act2.team_id = self.team1
            self.act2.user_id = self.employee

    def test_missing_activities(self):
        self.assertFalse(self.act1.team_id, "Error: Activity 1 should not have a team.")
        self.assertEqual(self.team1.count_missing_activities, 1)
        self.team1.assign_team_to_unassigned_activities()
        self.team1._compute_missing_activities()
        self.assertEqual(self.team1.count_missing_activities, 0)
        self.assertEqual(self.act1.team_id, self.team1)

    def test_leader_onchange(self):
        self.team2.user_id = self.employee3
        self.team2._onchange_user_id()
        self.assertTrue(self.employee3 in self.team2.member_ids)

    def test_activity_onchanges_keep_user(self):
        self.assertEqual(
            self.act2.team_id, self.team1, "Error: Activity 2 should have Team 1."
        )
        with Form(self.act2) as form:
            form.team_id = self.env["mail.activity.team"]
            self.assertEqual(form.user_id, self.employee)

    def test_activity_onchanges_user_no_member_team(self):
        self.assertEqual(
            self.act2.team_id, self.team1, "Error: Activity 2 should have Team 1."
        )
        with self.assertRaises(
            AssertionError, msg="can't write on invisible field user_id"
        ):
            with Form(self.act2) as form:
                form.user_id = self.employee2

    def test_activity_onchanges_user_no_team(self):
        self.assertEqual(
            self.act2.team_id, self.team1, "Error: Activity 2 should have Team 1."
        )
        with Form(self.act2) as form:
            form.team_id = self.env["mail.activity.team"]
            form.user_id = self.employee2
            self.assertEqual(form.team_id, self.team2)

    def test_activity_onchanges_team_no_member(self):
        self.assertEqual(
            self.act2.team_id, self.team1, "Error: Activity 2 should have Team 1."
        )
        self.team2.user_id = False
        self.team2.member_ids = False
        with Form(self.act2) as form:
            form.team_id = self.team2
            self.assertFalse(form.user_id)

    def test_activity_onchanges_team_different_member(self):
        self.assertEqual(
            self.act2.team_id, self.team1, "Error: Activity 2 should have Team 1."
        )
        self.team2.user_id = self.employee2
        self.team2.member_ids = self.employee2
        with Form(self.act2) as form:
            form.team_id = self.team2
            self.assertEqual(form.user_id, self.employee2)

    def test_activity_onchanges_team_different_member_no_leader(self):
        self.assertEqual(
            self.act2.team_id, self.team1, "Error: Activity 2 should have Team 1."
        )
        self.team2.user_id = False
        self.team2.member_ids = self.employee2
        with Form(self.act2) as form:
            form.team_id = self.team2
            self.assertEqual(form.user_id, self.employee2)

    def test_activity_onchanges_activity_type_set_team(self):
        self.assertEqual(
            self.act2.team_id, self.team1, "Error: Activity 2 should have Team 1."
        )
        self.activity1.default_team_id = self.team2
        self.assertEqual(self.act2.activity_type_id, self.activity2)
        with Form(self.act2) as form:
            form.activity_type_id = self.activity1
            self.assertEqual(form.team_id, self.team2)

    def test_activity_onchanges_activity_type_no_team(self):
        self.assertEqual(
            self.act2.team_id, self.team1, "Error: Activity 2 should have Team 1."
        )
        self.assertEqual(self.act2.activity_type_id, self.activity2)
        with Form(self.act2) as form:
            form.activity_type_id = self.activity1
            self.assertEqual(form.team_id, self.team1)

    def test_activity_constrain(self):
        with self.assertRaises(ValidationError):
            self.act2.write({"user_id": self.employee2.id, "team_id": self.team1.id})

    def test_schedule_activity(self):
        """Correctly assign teams to auto scheduled activities. Those won't
        trigger onchanges and could raise constraints and team missmatches"""
        partner_record = self.employee.partner_id.with_user(self.employee.id)
        activity = partner_record.activity_schedule(
            user_id=self.employee2.id,
            activity_type_id=self.env.ref("mail.mail_activity_data_call").id,
        )
        self.assertEqual(activity.team_id, self.team2)

    def test_schedule_activity_default_team(self):
        """Correctly assign teams to auto scheduled activities. Those won't
        trigger onchanges and could raise constraints and team missmatches"""
        partner_record = self.employee.partner_id.with_user(self.employee.id)
        self.env.ref("mail.mail_activity_data_call").default_team_id = self.team2
        activity = partner_record.activity_schedule(
            act_type_xmlid="mail.mail_activity_data_call",
        )
        self.assertEqual(activity.team_id, self.team2)
        # As we are in a 'team activity' context, the user should not be set
        self.assertEqual(activity.user_id, self.env["res.users"])

    def test_schedule_activity_default_team_no_user(self):
        """Correctly assign teams to auto scheduled activities. Those won't
        trigger onchanges and could raise constraints and team missmatches"""
        partner_record = self.employee.partner_id.with_user(self.employee.id)
        self.activity2.default_team_id = self.team2
        self.team2.member_ids = self.employee2
        activity = partner_record.activity_schedule(
            activity_type_id=self.activity2.id,
        )
        self.assertEqual(activity.team_id, self.team2)
        # As we are in a 'team activity' context, the user should not be set
        self.assertEqual(activity.user_id, self.env["res.users"])

    def test_schedule_activity_no_default_team(self):
        """If there are no teams, activities can still be scheduled for users"""
        self.env["mail.activity.team"].search([]).unlink()
        partner_record = self.employee.partner_id.with_user(self.employee.id)
        activity = partner_record.activity_schedule(
            activity_type_id=self.activity2.id,
            user_id=self.employee2.id,
        )
        self.assertFalse(activity.team_id)
        self.assertEqual(activity.user_id, self.employee2)

    def test_activity_count(self):
        res = (
            self.env["res.users"]
            .with_user(self.employee.id)
            .with_context(**{"team_activities": True})
            ._get_activity_groups()
        )
        self.assertEqual(res[0]["total_count"], 0)
        self.assertEqual(res[0]["today_count"], 1)
        partner_record = self.employee.partner_id.with_user(self.employee.id)
        self.activity2.default_team_id = self.team2
        activity = partner_record.activity_schedule(
            activity_type_id=self.activity2.id, user_id=self.employee2.id
        )
        activity.flush_recordset()
        res = (
            self.env["res.users"]
            .with_user(self.employee.id)
            .with_context(**{"team_activities": True})
            ._get_activity_groups()
        )
        self.assertEqual(res[0]["total_count"], 1)
        self.assertEqual(res[0]["today_count"], 2)
        res = self.env["res.users"].with_user(self.employee.id)._get_activity_groups()
        self.assertEqual(res[0]["total_count"], 2)

    def test_activity_schedule_next(self):
        self.activity1.write(
            {
                "default_team_id": self.team1.id,
                "triggered_next_type_id": self.activity2.id,
            }
        )
        self.activity2.default_team_id = self.team2
        self.team2.member_ids = self.employee2
        partner_record = self.employee.partner_id.with_user(self.employee.id)
        activity = partner_record.activity_schedule(activity_type_id=self.activity1.id)
        activity.flush_recordset()
        _messages, next_activities = activity._action_done()
        self.assertTrue(next_activities)
        self.assertEqual(next_activities.team_id, self.team2)
        # As we are in a 'team activity' context, the user should not be set
        self.assertEqual(next_activities.user_id, self.env["res.users"])

    def test_schedule_activity_from_server_action(self):
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        action = self.env["ir.actions.server"].create(
            {
                "name": "Test Server Action",
                "model_id": self.partner_ir_model.id,
                "state": "next_activity",
                "activity_type_id": self.activity1.id,
                "activity_user_type": "specific",
                "activity_user_id": self.employee.id,
                "activity_team_id": self.team1.id,
            }
        )
        action.with_context(active_model=partner._name, active_ids=partner.ids).run()
        self.assertEqual(partner.activity_ids[-1].team_id, self.team1)
        action.activity_team_id = self.team2
        action.with_context(active_model=partner._name, active_ids=partner.ids).run()
        self.assertEqual(partner.activity_ids[-1].team_id, self.team2)

    def test_server_action_onchanges_activity_team_id_activity_user_id(self):
        self.team1.user_id = self.team1.member_ids[0]
        server_action = self.env["ir.actions.server"].create(
            {
                "name": "Test Server Action 2",
                "model_id": self.partner_ir_model.id,
                "state": "next_activity",
                "activity_type_id": self.activity2.id,
                "activity_user_type": "specific",
                "activity_user_id": self.employee.id,
            }
        )
        with Form(server_action) as form:
            form.activity_team_id = self.team1
            self.assertEqual(form.activity_user_id, self.team1.user_id)

    def test_my_activity_date_deadline(self):
        """This test case checks
        - if the team activities are properly filtered
        """
        today = date.today()
        self.act2.write(
            {
                "user_id": False,
                "team_id": self.team1.id,
                "date_deadline": today,
            }
        )
        partner = (
            self.env["res.partner"]
            .with_context(team_activities=True)
            .with_user(self.employee.id)
            .search([("my_activity_date_deadline", "=", today)])
        )
        self.assertEqual(partner, self.partner_client)
        self.assertEqual(partner.my_activity_date_deadline, today)

    def _web_search_read_to_ids(self, domain, context=None):
        """Return web_search_read results as a set of ids"""
        if context is None:
            context = {}
        res = (
            self.env["res.partner"]
            .with_context(**context)
            .web_search_read(
                domain,
                {"id": {}},
            )
        )
        return set(record["id"] for record in res["records"])

    def test_web_search_read(self):
        """Test the domain mangling of web_search_read"""
        # Create a non-team activity for our second employee, for a second partner
        self.team1.member_ids |= self.employee2
        partner2 = self.partner_client.copy()
        self.employee2.groups_id += self.env.ref("base.group_partner_manager")

        # Craft the activity without a team
        act3 = (
            self.env["mail.activity"]
            .with_user(self.employee2)
            .create(
                {
                    "activity_type_id": self.activity1.id,
                    "note": "Partner activity 3.",
                    "res_id": partner2.id,
                    "res_model_id": self.partner_ir_model.id,
                    "team_user_id": self.employee2.id,
                    "user_id": self.employee2.id,
                    "team_id": False,
                }
            )
        )
        self.assertFalse(act3.team_id)

        # A regular search retrieves this activity
        self.assertEqual(
            self._web_search_read_to_ids(
                [("activity_user_id", "=", self.employee2.id)]
            ),
            set(partner2.ids),
        )

        # Searching with magic context key retrieves team activities.
        self.assertEqual(
            self._web_search_read_to_ids(
                [("activity_user_id", "=", self.employee2.id)],
                {"team_activities": True},
            ),
            set(self.partner_client.ids),
        )

    def test_migration(self):
        """Check that the 18.0.1.0.0 migration script runs without error"""
        rule = self.env.ref("mail_activity_team.mail_activity_rule_my_team")
        rule.perm_create = True

        # Run the migration script
        pyfile = os.path.join(
            "mail_activity_team",
            "migrations",
            "18.0.1.0.0",
            "post-migration.py",
        )
        name, ext = os.path.splitext(os.path.basename(pyfile))
        mod = load_script(pyfile, name)
        mod.migrate(self.env.cr, "18.0.1.0.0")

        self.assertFalse(rule.perm_create)
