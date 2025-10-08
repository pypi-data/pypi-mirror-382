# Copyright 2020 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import re
import unittest
import uuid
from pathlib import Path

import yaml
from deepdiff import DeepDiff
from fs.tempfs import TempFS

from cosl.juju_topology import JujuTopology
from cosl.rules import AlertRules


class TestEndpointProvider(unittest.TestCase):
    def test_each_alert_rule_is_topology_labeled(self):
        ri = AlertRules(
            query_type="promql",
            topology=JujuTopology(
                model="unittest",
                model_uuid=str(uuid.uuid4()),
                unit="tester/0",
                application="tester",
            ),
        )
        ri.add_path(Path(__file__).resolve().parent / "promql_rules" / "prometheus_alert_rules")

        alerts = ri.as_dict()
        self.assertIn("groups", alerts)
        self.assertEqual(len(alerts["groups"]), 5)
        for group in alerts["groups"]:
            for rule in group["rules"]:
                if "and_unit" not in group["name"]:
                    self.assertIn("labels", rule)
                    labels = rule["labels"]
                    self.assertIn("juju_model", labels)
                    self.assertIn("juju_application", labels)
                    self.assertIn("juju_model_uuid", labels)
                    # alerts should not have unit information if not already present
                    # https://discourse.charmhub.io/t/juju-topology-labels/8874
                    self.assertNotIn("juju_unit", rule["labels"])
                    self.assertNotIn("juju_unit=", rule["expr"])
                else:
                    self.assertIn("labels", rule)
                    labels = rule["labels"]
                    self.assertIn("juju_model", labels)
                    self.assertIn("juju_application", labels)
                    self.assertIn("juju_model_uuid", labels)
                    # unit information is already present
                    self.assertIn("juju_unit", rule["labels"])
                    self.assertIn("juju_unit=", rule["expr"])

    def test_each_alert_expression_is_topology_labeled(self):
        ri = AlertRules(
            query_type="promql",
            topology=JujuTopology(
                model="unittest",
                model_uuid=str(uuid.uuid4()),
                unit="tester/0",
                application="tester",
            ),
        )
        ri.add_path(Path(__file__).resolve().parent / "promql_rules" / "prometheus_alert_rules")

        alerts = ri.as_dict()
        self.assertIn("groups", alerts)
        self.assertEqual(len(alerts["groups"]), 5)
        group = alerts["groups"][0]
        for rule in group["rules"]:
            self.assertIn("expr", rule)
            for labels in expression_labels(rule["expr"]):
                self.assertIn("juju_model", labels)
                self.assertIn("juju_model_uuid", labels)
                self.assertIn("juju_application", labels)


class TestAddRuleFromStr(unittest.TestCase):
    def setUp(self):
        self.rule = {
            "alert": "SomeRuleName",
            "expr": "up < 1",
            "labels": {"severity": "critical"},
        }

    def test_official_rule_add_alerts_from_dict(self):
        official_rule = {
            "groups": [
                {
                    "name": "SomeGroupName",
                    "rules": [
                        {
                            "alert": "FooRule",
                            "expr": "up < 1",
                            "labels": {"severity": "critical"},
                        },
                        {
                            "alert": "BarRule",
                            "expr": "absent(up)",
                            "labels": {"severity": "critical"},
                        },
                    ],
                }
            ]
        }
        expected_rules = {
            "groups": [
                {
                    "name": "initial_alerts",
                    "rules": [self.rule],
                },
                {"name": "SomeGroupName_alerts", "rules": official_rule["groups"][0]["rules"]},
            ]
        }
        # GIVEN an alert rule
        rules = AlertRules(query_type="promql")
        rules.groups = rules._from_dict(self.rule, group_name="initial")
        # WHEN a rule is added from string in official-rule format
        rules.add(official_rule)
        rules_dict = rules.as_dict()
        # THEN the new rule is a combination of all
        self.assertEqual({}, DeepDiff(expected_rules, rules_dict))

    def test_single_rule_add_alerts_from_dict(self):
        single_rule = {
            "alert": "BarRule",
            "expr": "up < 1",
            "labels": {"severity": "critical"},
        }
        expected_rules = {
            "groups": [
                {
                    "name": "initial_alerts",
                    "rules": [self.rule],
                },
                {"name": "some_new_alerts", "rules": [single_rule]},
            ]
        }
        # GIVEN an alert rule
        rules = AlertRules(query_type="promql")
        rules.groups = rules._from_dict(self.rule, group_name="initial")
        # WHEN a rule is added from string in single-rule format with a custom group name and prefix
        rules.add(
            single_rule,
            group_name="new",
            group_name_prefix="some",
        )
        # THEN the new rule is a combination of all
        rules_dict = rules.as_dict()
        # AND the added rule group name has the custom group name and prefix
        self.assertEqual({}, DeepDiff(expected_rules, rules_dict))


class TestFromDictGroupName(unittest.TestCase):
    def setUp(self):
        self.official_rule = {
            "groups": [
                {
                    "name": "SomeGroupName",
                    "rules": [
                        {
                            "alert": "SomeRuleName",
                            "expr": "up < 1",
                            "labels": {"severity": "critical"},
                        }
                    ],
                }
            ]
        }
        self.single_rule = {
            "alert": "SomeRuleName",
            "expr": "up < 1",
            "labels": {"severity": "critical"},
        }

    def test_single_rule_from_dict_group_sanitized(self):
        # GIVEN an alert rule in single-rule format
        rules = AlertRules(query_type="promql")
        # WHEN processed as string and provided an illegal custom group name
        groups = rules._from_dict(
            self.single_rule, group_name="Foo$123/Hello:World(go_od)bye!@#^&*()[]{}|;:,.<>?`~_"
        )
        for group in groups:
            # THEN the group name only contains characters in [a-zA-Z0-9_:]
            # AND special characters are replaced with "_"
            self.assertEqual(
                group["name"], "Foo_123_Hello:World_go_od_bye______________:_________alerts"
            )

    def test_single_rule_from_dict(self):
        # GIVEN an alert rule in single-rule format
        rules = AlertRules(query_type="promql")
        # WHEN processed as string
        groups = rules._from_dict(self.single_rule)
        for group in groups:
            # THEN group name contains hash
            self.assertNotEqual(get_hash(group["name"]), "")

    def test_single_rule_from_dict_custom_group(self):
        # GIVEN an alert rule in single-rule format
        rules = AlertRules(query_type="promql")
        # WHEN processed as string and provided custom group name
        groups = rules._from_dict(self.single_rule, group_name="foo")
        for group in groups:
            # THEN group name does not contain hash
            self.assertEqual(get_hash(group["name"]), "")
            # AND group name contains the custom group name
            self.assertIn("foo", group["name"])

    def test_single_rule_from_dict_custom_group_prefix(self):
        # GIVEN an alert rule in single-rule format
        rules = AlertRules(query_type="promql")
        # WHEN processed as string and provided custom group name prefix
        groups = rules._from_dict(self.single_rule, group_name_prefix="foo")
        for group in groups:
            # THEN group name does not include the original group name
            self.assertNotIn("SomeGroupName", group["name"])
            # AND group name is prefixed with custom value
            self.assertTrue(group["name"].startswith("foo"))

    def test_official_rule_from_dict(self):
        # GIVEN an alert rule in official-rule format
        rules = AlertRules(query_type="promql")
        # WHEN processed as dict
        groups = rules._from_dict(self.official_rule)
        for group in groups:
            # THEN group name matches the group name in the alert
            self.assertIn("SomeGroupName", group["name"])

    def test_official_rule_from_dict_custom_group_prefix(self):
        # GIVEN an alert rule in official-rule format
        rules = AlertRules(query_type="promql")
        # WHEN processed as string and provided custom group name prefix
        groups = rules._from_dict(self.official_rule, group_name_prefix="foo")
        for group in groups:
            # THEN group name includes the original group name
            self.assertIn("SomeGroupName", group["name"])
            # AND group name is prefixed with custom value
            self.assertTrue(group["name"].startswith("foo"))

    def test_raises_value_error_empty_dict(self):
        rules = AlertRules(query_type="promql")
        with self.assertRaises(ValueError) as ctx:
            rules._from_dict("")
        self.assertEqual(str(ctx.exception), "Empty")

    def test_raises_value_error_invalid_rule_format(self):
        invalid_rule = {
            "expr": "up < 1",
            "labels": {"severity": "critical"},
        }
        rules = AlertRules(query_type="promql")
        with self.assertRaises(ValueError) as ctx:
            rules._from_dict(invalid_rule)
        self.assertEqual(str(ctx.exception), "Invalid rule format")


def sorted_matchers(matchers) -> str:
    parts = [m.strip() for m in matchers.split(",")]
    return ",".join(sorted(parts))


def expression_labels(expr):
    """Extract labels from an alert rule expression.

    Args:
        expr: a string representing an alert expression.

    Returns:
        a generator which yields each set of labels in
        in the expression.
    """
    pattern = re.compile(r"\{.*\}")
    matches = pattern.findall(expr)
    for match in matches:
        match = match.replace("=", '":').replace("juju_", '"juju_')
        labels = json.loads(match)
        yield labels


def get_hash(group_name: str) -> str:
    """Extract the hash of the group name when a group name was not provided to _from_dict method in the Rules class.

    This occurs when the single-rule format is provided rather than official-rule format.

    Args:
        group_name: a string representing the group name of the rules.

    Returns:
        the matching hexdigest of the group name if a match is found, otherwise an empty string.
    """
    import re

    pattern = r"([a-f0-9]{20})_"
    match = re.search(pattern, group_name)
    if match:
        return match.group(1)
    else:
        return ""


class TestAlertRulesWithOneRulePerFile(unittest.TestCase):
    def setUp(self) -> None:
        free_standing_rule = {
            "alert": "free_standing",
            "expr": "avg(some_vector[5m]) > 5",
        }

        alert_rule = {
            "alert": "CPUOverUse",
            "expr": "process_cpu_seconds_total{%%juju_topology%%} > 0.12",
        }
        rules_file_dict = {"groups": [{"name": "group1", "rules": [alert_rule]}]}

        self.sandbox = TempFS("rule_files", auto_clean=True)
        self.addCleanup(self.sandbox.close)
        self.sandbox.makedirs("rules/prom/mixed_format")
        self.sandbox.makedirs("rules/prom/lma_format")
        self.sandbox.makedirs("rules/prom/prom_format")
        self.sandbox.writetext("rules/prom/mixed_format/lma_rule.rule", yaml.safe_dump(alert_rule))
        self.sandbox.writetext(
            "rules/prom/mixed_format/standard_rule.rule", yaml.safe_dump(rules_file_dict)
        )
        self.sandbox.writetext(
            "rules/prom/lma_format/free_standing_rule.rule", yaml.safe_dump(free_standing_rule)
        )
        self.sandbox.writetext(
            "rules/prom/prom_format/standard_rule.rule", yaml.safe_dump(rules_file_dict)
        )

        self.topology = JujuTopology(
            "MyModel", "12de4fae-06cc-4ceb-9089-567be09fec78", "MyApp", "MyUnit", "MyCharm"
        )

    def test_non_recursive_is_default(self):
        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(self.sandbox.getsyspath("/rules/prom/"))
        rules_file_dict = rules.as_dict()
        self.assertEqual({}, rules_file_dict)

    def test_non_recursive_lma_format_loading_from_root_dir(self):
        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(self.sandbox.getsyspath("/rules/prom/lma_format/"))
        rules_file_dict = rules.as_dict()

        expected_freestanding_rule = {
            "alert": "free_standing",
            "expr": "avg(some_vector[5m]) > 5",
            "labels": self.topology.label_matcher_dict,
        }

        expected_rules_file = {
            "groups": [
                {
                    "name": f"{sorted_matchers(self.topology.identifier)}_free_standing_rule_alerts",
                    "rules": [expected_freestanding_rule],
                },
            ]
        }

        self.assertEqual(expected_rules_file, rules_file_dict)

    def test_non_recursive_official_format_loading_from_root_dir(self):
        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(self.sandbox.getsyspath("/rules/prom/prom_format"))
        rules_file_dict = rules.as_dict()

        expected_alert_rule = {
            "alert": "CPUOverUse",
            "expr": f"process_cpu_seconds_total{{{sorted_matchers(self.topology.alert_expression_str)}}} > 0.12",
            "labels": self.topology.label_matcher_dict,
        }

        expected_rules_file = {
            "groups": [
                {
                    "name": f"{self.topology.identifier}_group1_alerts",
                    "rules": [expected_alert_rule],
                },
            ]
        }
        self.assertEqual(expected_rules_file, rules_file_dict)

    def test_alerts_in_both_formats_are_recursively_aggregated(self):
        """This test covers several aspects of the rules format.

        - Group name:
          - For rules in lma format, core group name is the filename
          - For rules in official format, core group name is the group name in the file
        """
        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(self.sandbox.getsyspath("/rules/prom"), recursive=True)
        rules_file_dict = rules.as_dict()

        expected_alert_rule = {
            "alert": "CPUOverUse",
            "expr": f"process_cpu_seconds_total{{{sorted_matchers(self.topology.alert_expression_str)}}} > 0.12",
            "labels": self.topology.label_matcher_dict,
        }

        expected_freestanding_rule = {
            "alert": "free_standing",
            "expr": "avg(some_vector[5m]) > 5",
            "labels": self.topology.label_matcher_dict,
        }

        expected_rules_file = {
            "groups": [
                {
                    "name": f"{self.topology.identifier}_mixed_format_group1_alerts",
                    "rules": [expected_alert_rule],
                },
                {
                    "name": f"{self.topology.identifier}_mixed_format_lma_rule_alerts",
                    "rules": [expected_alert_rule],
                },
                {
                    "name": f"{self.topology.identifier}_lma_format_free_standing_rule_alerts",
                    "rules": [expected_freestanding_rule],
                },
                {
                    "name": f"{self.topology.identifier}_prom_format_group1_alerts",
                    "rules": [expected_alert_rule],
                },
            ]
        }

        self.assertEqual({}, DeepDiff(expected_rules_file, rules_file_dict, ignore_order=True))

    def test_unit_not_in_alert_labels(self):
        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(self.sandbox.getsyspath("/rules/prom"), recursive=True)
        rules_file_dict = rules.as_dict()
        for group in rules_file_dict["groups"]:
            for rule in group["rules"]:
                self.assertTrue("juju_unit" not in rule["labels"])

    def test_charm_not_in_alert_expression(self):
        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(self.sandbox.getsyspath("/rules/prom"), recursive=True)
        rules_file_dict = rules.as_dict()
        for group in rules_file_dict["groups"]:
            for rule in group["rules"]:
                self.assertTrue("charm=" not in rule["expr"])


class TestAlertRulesWithMultipleRulesPerFile(unittest.TestCase):
    def setUp(self) -> None:
        self.topology = JujuTopology(
            "MyModel", "12de4fae-06cc-4ceb-9089-567be09fec78", "MyApp", "MyCharm"
        )

    def gen_rule(self, name, **extra):
        return {
            "alert": f"CPUOverUse_{name}",
            "expr": f"process_cpu_seconds_total{{{sorted_matchers(self.topology.label_matchers)}}} > 0.12",
            **extra,
        }

    def gen_group(self, name):
        return {"name": f"group_{name}", "rules": [self.gen_rule(1), self.gen_rule(2)]}

    def test_load_multiple_rules_per_file(self):
        """Test official format with multiple alert rules per group in multiple groups."""
        rules_file_dict = {"groups": [self.gen_group(1), self.gen_group(2)]}
        sandbox = TempFS("rule_files", auto_clean=True)
        sandbox.makedirs("rules")
        sandbox.writetext("rules/file.rule", yaml.safe_dump(rules_file_dict))

        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(sandbox.getsyspath("/rules"), recursive=False)
        rules_file_dict_read = rules.as_dict()

        expected_rules_file = {
            "groups": [
                {
                    "name": f"{self.topology.identifier}_group_1_alerts",
                    "rules": [
                        self.gen_rule(1, labels=self.topology.label_matcher_dict),
                        self.gen_rule(2, labels=self.topology.label_matcher_dict),
                    ],
                },
                {
                    "name": f"{self.topology.identifier}_group_2_alerts",
                    "rules": [
                        self.gen_rule(1, labels=self.topology.label_matcher_dict),
                        self.gen_rule(2, labels=self.topology.label_matcher_dict),
                    ],
                },
            ]
        }
        self.assertDictEqual(expected_rules_file, rules_file_dict_read)

    def test_duplicated_alert_names_within_alert_rules_list_are_silently_accepted(self):
        """Test official format when the alert rules list has a duplicated alert name."""
        rules_file_dict = {
            "groups": [
                {
                    "name": "my_group",
                    "rules": [self.gen_rule("same"), self.gen_rule("same")],
                }
            ]
        }
        sandbox = TempFS("rule_files", auto_clean=True)
        sandbox.makedirs("rules")
        sandbox.writetext("rules/file.rule", yaml.safe_dump(rules_file_dict))

        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(sandbox.getsyspath("/rules"), recursive=False)
        rules_file_dict_read = rules.as_dict()

        expected_rules_file = {
            "groups": [
                {
                    "name": f"{self.topology.identifier}_my_group_alerts",
                    "rules": [
                        self.gen_rule("same", labels=self.topology.label_matcher_dict),
                        self.gen_rule("same", labels=self.topology.label_matcher_dict),
                    ],
                },
            ]
        }
        self.assertDictEqual(expected_rules_file, rules_file_dict_read)

    def test_duplicated_group_names_within_a_file_are_silently_accepted(self):
        rules_file_dict = {"groups": [self.gen_group("same"), self.gen_group("same")]}
        sandbox = TempFS("rule_files", auto_clean=True)
        sandbox.makedirs("rules")
        sandbox.writetext("rules/file.rule", yaml.safe_dump(rules_file_dict))

        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(sandbox.getsyspath("/rules"), recursive=False)
        rules_file_dict_read = rules.as_dict()

        expected_rules_file = {
            "groups": [
                {
                    "name": f"{self.topology.identifier}_group_same_alerts",
                    "rules": [
                        self.gen_rule(1, labels=self.topology.label_matcher_dict),
                        self.gen_rule(2, labels=self.topology.label_matcher_dict),
                    ],
                },
                {
                    "name": f"{self.topology.identifier}_group_same_alerts",
                    "rules": [
                        self.gen_rule(1, labels=self.topology.label_matcher_dict),
                        self.gen_rule(2, labels=self.topology.label_matcher_dict),
                    ],
                },
            ]
        }
        self.assertDictEqual(expected_rules_file, rules_file_dict_read)

    def test_deeply_nested(self):
        sandbox = TempFS("rule_files", auto_clean=True)
        sandbox.makedirs("rules/a/b/")
        sandbox.writetext("rules/file.rule", yaml.safe_dump(self.gen_rule(0)))
        sandbox.writetext("rules/a/file.rule", yaml.safe_dump(self.gen_rule(1)))
        sandbox.writetext("rules/a/b/file.rule", yaml.safe_dump(self.gen_rule(2)))

        rules = AlertRules(query_type="promql", topology=self.topology)
        rules.add_path(sandbox.getsyspath("/rules"), recursive=True)
        rules_file_dict_read = rules.as_dict()

        expected_rules_file = {
            "groups": [
                {
                    "name": f"{self.topology.identifier}_file_alerts",
                    "rules": [self.gen_rule(0, labels=self.topology.label_matcher_dict)],
                },
                {
                    "name": f"{self.topology.identifier}_a_file_alerts",
                    "rules": [self.gen_rule(1, labels=self.topology.label_matcher_dict)],
                },
                {
                    "name": f"{self.topology.identifier}_a_b_file_alerts",
                    "rules": [self.gen_rule(2, labels=self.topology.label_matcher_dict)],
                },
            ]
        }
        self.assertDictEqual(expected_rules_file, rules_file_dict_read)


class TestAlertRulesContainingUnitTopology(unittest.TestCase):
    """Tests that check we does not remove unit topology.

    Unit Topology information is not added to alert rules expressions and labels,
    by the Provider. However, if unit topology information is
    present in the labels then it must not be removed since the client that
    the alert be limited to a specific unit.
    """

    def test_unit_label_is_retained_if_hard_coded(self):
        ri = AlertRules(
            query_type="promql",
            topology=JujuTopology(
                model="unittest",
                model_uuid=str(uuid.uuid4()),
                unit="tester/0",
                application="tester",
            ),
        )
        ri.add_path(
            Path(__file__).resolve().parent / "promql_rules" / "alert_rules_with_unit_topology"
        )

        alert_rules = ri.as_dict()
        for group in alert_rules["groups"]:
            for rule in group["rules"]:
                self.assertIn("juju_unit", rule["labels"])
                self.assertIn("juju_unit=", rule["expr"])
