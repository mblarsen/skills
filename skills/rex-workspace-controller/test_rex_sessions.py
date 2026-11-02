"""Regression tests; all Rex subprocesses are mocked, so no live panes change."""
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


if __name__ == "__main__":
    unittest.main()
