"""异常取证与分享报告只使用临时目录；进程级钩子在子进程里验证。"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from peach import error_reporting, support_bundle

ROOT = Path(__file__).resolve().parents[1]


class ErrorReportingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.logs = self.root / "logs"
        self.addCleanup(mock.patch.stopall)
        mock.patch.dict(os.environ, {"PEACH_DATA_ROOT": str(self.root)}).start()
        mock.patch.object(error_reporting, "_log_dir", self.logs).start()

    def probe(self, code):
        return subprocess.run([sys.executable, "-X", "utf8", "-c", code],
                              env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
                              capture_output=True, text=True, encoding="utf-8", timeout=30)

    def records(self):
        return [json.loads(line) for path in self.logs.glob("errors-*.log")
                for line in path.read_text(encoding="utf-8").splitlines()]

    def test_uncaught_import_and_thread_failures_are_saved_without_a_console(self):
        result = self.probe("import sys, threading; from peach import error_reporting as e; "
                            "e.install(); sys.stderr=None; "
                            "t=threading.Thread(target=lambda: 1/0, name='worker'); t.start(); t.join(); "
                            "import peach_missing_startup_dependency")
        self.assertNotEqual(result.returncode, 0)
        events = self.records()
        stages = {row["stage"] for row in events}
        self.assertTrue({"entry", "unhandled-main", "unhandled-thread"} <= stages)
        failure = next(row for row in events if row["stage"] == "unhandled-main")
        self.assertEqual(failure["exception"][0]["type"], "ModuleNotFoundError")
        self.assertTrue(failure["frames"])

    def test_native_traceback_handler_is_enabled_and_writes_to_a_file(self):
        result = self.probe("import faulthandler; from peach import error_reporting as e; "
                            "e.install(); assert faulthandler.is_enabled(); "
                            "faulthandler.dump_traceback(file=e._fault_stream)")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(any('line' in path.read_text(encoding="utf-8") for path in self.logs.glob("crash-*.log")))

    def test_exception_records_keep_codes_and_frames_without_source_lines_or_credentials(self):
        try:
            raise OSError(5, 'password=private-password https://example.com/?token=private-token')
        except OSError as error:
            error.peach_operation = "OpenProcess(desktop)"
            path = error_reporting.event("tray-handoff", error)
        row = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(row["exception"][0]["errno"], 5)
        self.assertEqual(row["exception"][0]["operation"], "OpenProcess(desktop)")
        self.assertTrue(row["frames"])
        self.assertNotIn("private-password", path.read_text(encoding="utf-8"))
        self.assertNotIn("private-token", path.read_text(encoding="utf-8"))

    def test_unwritable_log_directory_uses_the_temporary_fallback(self):
        blocked = self.root / "blocked"
        blocked.write_text("file", encoding="utf-8")
        fallback = self.root / "fallback"
        with mock.patch.object(error_reporting, "log_directories", return_value=[blocked / "logs", fallback]):
            path = error_reporting.event("entry")
        self.assertEqual(path.parent, fallback)
        self.assertTrue(path.is_file())

    def test_shared_job_failure_context_is_preserved_in_the_redacted_report(self):
        error = OSError("desktop process creation denied")
        error.peach_operation = "CreateProcessW(breakaway)"
        error.peach_context = {
            "caller": {"pid": 123, "in_job": True, "immediate_limit_flags": "0x2000",
                       "immediate_limit_names": ["KILL_ON_JOB_CLOSE"]},
            "desktop": {"pid": 456, "in_job": True},
            "job_chain": {"status": "unavailable"}, "token": "private-job-token"}
        error_reporting.event("tray-handoff", error)
        with zipfile.ZipFile(io.BytesIO(support_bundle.bundle_bytes())) as archive:
            name = next(name for name in archive.namelist() if 'errors-' in name)
            payload = archive.read(name).decode()
        context = json.loads(payload)["exception"][0]["context"]
        self.assertEqual(context["caller"], error.peach_context["caller"])
        self.assertEqual(context["desktop"], {"pid": 456, "in_job": True})
        self.assertEqual(context["job_chain"]["status"], "unavailable")
        self.assertNotIn("private-job-token", payload)

    def test_bundle_is_available_with_corrupt_configuration_and_excludes_private_files(self):
        (self.root / "config.toml").write_text('secret = "unclosed-private-config', encoding="utf-8")
        (self.root / "ledger.db").write_text("private-database", encoding="utf-8")
        self.logs.mkdir()
        (self.logs / "tray.log").write_text(
            'Cookie: session=private-session; other=private-cookie\n'
            'Authorization: Bearer private-auth\n'
            'password=private-password\n'
            'https://private.example/download?key=private-key\n'
            'C:\\Users\\private-user\\private.mp4\n'
            '/example/private-user/movie.mp4\n203.0.113.20\n'
            'user@private.example\n', encoding="utf-8")
        (self.logs / "unapproved.log").write_text("private-unapproved", encoding="utf-8")
        error_reporting.event("entry")
        with zipfile.ZipFile(io.BytesIO(support_bundle.bundle_bytes())) as archive:
            report = json.loads(archive.read("report.json"))
            contents = "\n".join(archive.read(name).decode() for name in archive.namelist())
            self.assertEqual(report["configuration"]["status"], "unavailable")
            self.assertTrue(all(name == "report.json" or name.startswith("logs/") for name in archive.namelist()))
            self.assertNotIn("unapproved.log", " ".join(archive.namelist()))
        for secret in ("private-session", "private-cookie", "private-auth", "private-password", "private-key",
                       "private.example", "private-user", "203.0.113.20", "private-database", "unclosed-private-config"):
            self.assertNotIn(secret, contents)

    def test_report_tail_is_bounded_and_records_the_truncation(self):
        self.logs.mkdir()
        (self.logs / "tray.log").write_bytes(b"discard-this\n" * 20_000 + b"final-error\n")
        with zipfile.ZipFile(io.BytesIO(support_bundle.bundle_bytes())) as archive:
            name = next(name for name in archive.namelist() if name.endswith("tray.log"))
            self.assertLessEqual(len(archive.read(name)), support_bundle.TAIL_BYTES)
            self.assertIn(b"final-error", archive.read(name))
            report = json.loads(archive.read("report.json"))
            self.assertTrue(next(row for row in report["logs"] if row["name"] == "tray.log")["truncated"])

    def test_prefixed_cookie_headers_and_arbitrary_absolute_paths_are_redacted(self):
        self.logs.mkdir()
        (self.logs / "tray.log").write_text(
            '2026-10-15 ERROR Cookie: SEID=private-a; CID=private-b; UID=private-c\n'
            '/data/private-user/movie.mp4\n/srv/private-user/movie.mp4\n', encoding="utf-8")
        with zipfile.ZipFile(io.BytesIO(support_bundle.bundle_bytes())) as archive:
            content = "\n".join(archive.read(name).decode() for name in archive.namelist())
        for secret in ("private-a", "private-b", "private-c", "private-user"):
            self.assertNotIn(secret, content)

    def test_warning_logs_keep_their_console_output_and_persistent_record(self):
        result = self.probe("import logging; from peach import error_reporting as e; "
                            "e.install(); logging.warning('warning example')")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("warning example", result.stderr)
        self.assertTrue(any(row.get("level") == "WARNING" for row in self.records()))

    def test_an_unusable_temporary_directory_does_not_disable_the_data_log_directory(self):
        with mock.patch.object(error_reporting.tempfile, "gettempdir", side_effect=FileNotFoundError("No usable temporary directory")):
            path = error_reporting.event("entry")
            report = support_bundle.save_bundle()
        self.assertEqual(path.parent, self.logs)
        self.assertTrue(zipfile.is_zipfile(report))

    def test_structured_log_export_preserves_frames_and_redacts_secret_fields(self):
        self.logs.mkdir()
        row = {"stage": "logging", "message": "Cookie: SEID=private-cookie; CID=private-cid",
               "exception": [{"type": "OSError", "winerror": 5}],
               "frames": [{"file": "tray.py", "line": 5}], "token": "private-token"}
        (self.logs / "errors-123.log").write_text(json.dumps(row) + "\n", encoding="utf-8")
        with zipfile.ZipFile(io.BytesIO(support_bundle.bundle_bytes())) as archive:
            name = next(name for name in archive.namelist() if name.endswith("errors-123.log"))
            content = archive.read(name).decode()
            exported = json.loads(content)
        self.assertEqual(exported["frames"], row["frames"])
        self.assertEqual(exported["exception"][0]["winerror"], 5)
        for secret in ("private-cookie", "private-cid", "private-token"):
            self.assertNotIn(secret, content)

    def test_failure_dialog_points_to_an_existing_report_and_cli_needs_no_service(self):
        message = error_reporting.failure_details("tray-handoff", OSError("desktop unavailable"))
        self.assertIn("诊断报告", message)
        self.assertEqual(len(list(self.logs.glob("peach-support-*.zip"))), 1)
        destination = self.root / "share.zip"
        result = self.probe(f"from peach.support_bundle import main; raise SystemExit(main([{str(destination)!r}]))")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(zipfile.is_zipfile(destination))
        again = self.probe(f"from peach.support_bundle import main; raise SystemExit(main([{str(destination)!r}]))")
        self.assertNotEqual(again.returncode, 0)

    def test_browser_errors_and_bundle_require_local_same_origin_access(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from types import SimpleNamespace
        from peach import routes_configuration
        from peach.routes_auth import require_auth
        app = FastAPI()
        app.include_router(routes_configuration.router)
        app.dependency_overrides[require_auth] = lambda: {}
        app.state.settings = SimpleNamespace(mdns_name="peach")
        app.state.mount_reachability = SimpleNamespace(summary=lambda: {})
        client = TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 1234))
        path = "/api/diagnostics/client-error"
        self.assertEqual(client.post(path, json={"message": "secret=private-browser"},
                                     headers={"Origin": "https://other.example"}).status_code, 403)
        self.assertEqual(client.post(path, content=b"x" * 20_000).status_code, 413)
        self.assertEqual(client.post(path, json={"message": 5}).status_code, 400)
        self.assertEqual(client.post(path, json={"message": "secret=private-browser", "stack": "at render"}).status_code, 200)
        browser = next(row for row in self.records() if row["stage"] == "browser")
        self.assertNotIn("private-browser", str(browser))
        self.assertEqual(browser["stack"], "at render")
        with mock.patch("peach.diagnostics.report", side_effect=RuntimeError("diagnostics unavailable")):
            response = client.get("/api/diagnostics/bundle")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertTrue(zipfile.is_zipfile(io.BytesIO(response.content)))
        remote = TestClient(app, base_url="http://127.0.0.1", client=("192.0.2.55", 1234))
        self.assertEqual(remote.post(path, json={"message": "example"}).status_code, 403)
        self.assertEqual(remote.get("/api/diagnostics/bundle").status_code, 403)
        for _ in range(20):
            response = client.post(path, json={"message": "example"})
        self.assertEqual(response.status_code, 429)

    def test_asyncio_exceptions_are_recorded_and_keep_the_default_handler(self):
        loop = mock.Mock()
        error_reporting.asyncio_handler(loop, {"exception": ValueError("async failure"), "message": "task"})
        self.assertEqual(self.records()[0]["stage"], "unhandled-asyncio")
        loop.default_exception_handler.assert_called_once()

    def test_unraisable_errors_and_logging_exceptions_have_persistent_records(self):
        code = """
import gc, logging, sys
from peach import error_reporting as e
e.install()
sys.stderr = None
class Broken:
    def __del__(self):
        raise RuntimeError('cleanup failed')
delayed = Broken()
del delayed
gc.collect()
try:
    raise ValueError('service failed')
except ValueError:
    logging.getLogger('peach.service').exception('request failed')
"""
        result = self.probe(code)
        self.assertEqual(result.returncode, 0, result.stderr)
        stages = {row["stage"] for row in self.records()}
        self.assertTrue({"unraisable", "logging"} <= stages)

    def test_packaged_tray_import_failure_saves_a_report_before_optional_dependencies(self):
        code = f"""
import builtins, ctypes, runpy, sys
from pathlib import Path
original = builtins.__import__
def import_module(name, *args, **kwargs):
    if name == 'pystray':
        raise ModuleNotFoundError('tray dependency unavailable')
    return original(name, *args, **kwargs)
builtins.__import__ = import_module
if sys.platform == 'win32':
    ctypes.windll.user32.MessageBoxW = lambda _, message, *rest: Path({str(self.root / 'dialog.txt')!r}).write_text(message, encoding='utf-8')
sys.argv = ['Peach.exe']
runpy.run_path({str(ROOT / 'scripts/build_app_entry.py')!r}, run_name='__main__')
"""
        result = self.probe(code)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(list(self.logs.glob("peach-support-*.zip")))
        self.assertTrue(any(row["stage"] == "tray-import" for row in self.records()))
        if sys.platform == "win32":
            self.assertIn("诊断报告", (self.root / "dialog.txt").read_text(encoding="utf-8"))

    def test_offline_export_creates_its_log_directory_on_a_fresh_machine(self):
        result = self.probe("from peach.support_bundle import main; raise SystemExit(main())")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(list(self.logs.glob("peach-support-*.zip")))


if __name__ == "__main__":
    unittest.main()
