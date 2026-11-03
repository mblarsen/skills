"""Regression tests; all Rex subprocesses are mocked, so no live panes change."""
import contextlib
import io
import importlib.machinery
import importlib.util
import pathlib
import unittest
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader(
    "rex_sessions", str(pathlib.Path(__file__).with_name("rex-sessions"))
)
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class SessionDetectionTests(unittest.TestCase):
    def test_up_inspects_session_with_positional_id_and_json(self):
        def fake_rex(*args):
            if args == ("session", "inspect", "session:test", "--json"):
                return {"session_id": "session:test"}
            raise RuntimeError("unsupported inspect arguments")

        with patch.object(module, "rex", side_effect=fake_rex), patch.object(
            module, "live_windows", return_value={}
        ):
            self.assertEqual(module.cmd_up({"rex_session": "session:test"}, [], True), 0)


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.doc = {"label": "work", "rex_session": "session:test", "panes": [
            {"window": "controller", "alias": "main", "stop": "keep", "restore": ["pi"]},
            {"window": "care-coordinators", "alias": "care-main", "restore": ["pi", "--session", "one"]},
            {"window": "care-coordinators", "alias": "care-reviewer", "restore": ["pi", "--session", "two"]},
            {"window": "other", "alias": "other-main", "restore": ["pi"]},
        ]}

    def test_exact_tab_and_alias_union_preserves_order(self):
        selected = module.select_panes(self.doc, ["other-main", "care-main"], ["care-coordinators"])
        self.assertEqual([p["alias"] for p in selected], ["care-main", "care-reviewer", "other-main"])
        self.assertEqual(module.select_panes(self.doc, [], []), self.doc["panes"])
        self.assertEqual(module.select_panes(self.doc, ["other-main"], []), self.doc["panes"][3:])

    def test_unknown_selector_fails_before_rex(self):
        for only, tabs in [(["care"], []), ([], ["missing"]), (["main", "missing"], [])]:
            for operation in ("up", "down"):
                with self.subTest(only=only, tabs=tabs, operation=operation), patch.object(module, "rex") as rex, patch.object(module, "live_windows") as live:
                    with self.assertRaises(SystemExit) as error:
                        if operation == "up":
                            module.cmd_up(self.doc, only, True, tabs)
                        else:
                            module.cmd_down(self.doc, only, False, True, tabs)
                    self.assertEqual(error.exception.code, 2)
                    rex.assert_not_called()
                    live.assert_not_called()

    def test_list_groups_saved_members_without_live_inspection(self):
        output = io.StringIO()
        with patch.object(module, "rex") as rex, contextlib.redirect_stdout(output):
            module.cmd_members(self.doc, module.select_panes(self.doc, [], ["care-coordinators"]))
        rex.assert_not_called()
        self.assertIn("[care-coordinators]", output.getvalue())
        self.assertIn("care-reviewer", output.getvalue())
        self.assertNotIn("other-main", output.getvalue())

    def test_main_routes_workspace_listing_without_rex(self):
        output = io.StringIO()
        with patch.object(module.sys, "argv", ["rex-sessions", "list", "work", "--tab=care-coordinators"]), patch.object(module, "resolve", return_value=pathlib.Path("work.toml")), patch.object(module, "read_toml", return_value=self.doc), patch.object(module, "rex") as rex, contextlib.redirect_stdout(output):
            self.assertEqual(module.main(), 0)
        rex.assert_not_called()
        self.assertIn("care-main", output.getvalue())
        self.assertNotIn("other-main", output.getvalue())

    def test_up_only_selected_tab_preserves_restore_and_skips_live_tab(self):
        with patch.object(module, "rex_quiet", return_value=True), patch.object(module, "live_windows", return_value={}), patch.object(module, "run", return_value=True) as run:
            module.cmd_up(self.doc, [], True, ["care-coordinators"])
            self.assertEqual(run.call_count, 2)
            commands = [call.args[0] for call in run.call_args_list]
            self.assertIn("care-coordinators", commands[0])
            self.assertEqual(commands[0][-3:], ["pi", "--session", "one"])
            self.assertEqual(commands[1][-3:], ["pi", "--session", "two"])
            self.assertEqual(commands[1][1], "split")
        with patch.object(module, "rex_quiet", return_value=True), patch.object(module, "live_windows", return_value={"care-coordinators": ["a", "b"]}), patch.object(module, "run") as run:
            module.cmd_up(self.doc, [], True, ["care-coordinators"])
            run.assert_not_called()

    def test_partial_split_and_drift_block_all_changes(self):
        for only, tabs, windows in [
            (["care-reviewer"], [], {}),
            (["care-main"], [], {"care-coordinators": ["a", "b"]}),
            ([], ["care-coordinators"], {"care-coordinators": ["survivor"]}),
        ]:
            for operation in ("up", "down"):
                with self.subTest(only=only, windows=windows, operation=operation), patch.object(module, "rex_quiet", return_value=True), patch.object(module, "live_windows", return_value=windows), patch.object(module, "run") as run:
                    # Include an earlier unrelated pane to check preflight is atomic.
                    with self.assertRaises(SystemExit):
                        if operation == "up":
                            module.cmd_up(self.doc, ["main", *only], True, tabs)
                        else:
                            module.cmd_down(self.doc, ["main", *only], False, True, tabs)
                    run.assert_not_called()

    def test_down_selected_tab_keeps_unrelated_panes(self):
        windows = {"controller": ["controller-id"], "care-coordinators": ["a", "b"], "other": ["other-id"]}
        with patch.object(module, "live_windows", return_value=windows), patch.object(module, "run", return_value=True) as run:
            module.cmd_down(self.doc, [], False, True, ["care-coordinators"])
            run.assert_called_once_with(["rex", "block", "close", "-s", "session:test", "a", "b"], True)
        with patch.object(module, "live_windows", return_value=windows), patch.object(module, "run") as run:
            module.cmd_down(self.doc, ["main"], False, True)
            run.assert_not_called()

    def test_parse_repeatable_selectors_and_usage_errors(self):
        self.assertEqual(module.parse(["up", "work", "--tab=care-coordinators", "--tab", "other", "--only", "main", "--dry-run"]),
                         ("up", "work", ["main"], ["care-coordinators", "other"], False, True, False))
        for args in (["up", "work", "--only"], ["up", "--tab="], ["up", "--tab", "--dry-run"], ["status", "work", "--only=main"], ["list", "--tab=other"]):
            with self.subTest(args=args), self.assertRaises(SystemExit) as error:
                module.parse(args)
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
