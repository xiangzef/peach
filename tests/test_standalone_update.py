"""独立包更新使用临时目录验证路径、进度、重启确认及回滚。"""
import json
import hashlib
import os
from contextlib import nullcontext
from pathlib import Path
import tempfile
import sqlite3
import unittest
from unittest.mock import Mock, patch
import zipfile

from peach import settings_file, standalone_update as update
from support.ledger import fresh_ledger


class StandaloneUpdateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.config = settings_file.load_config(environ={"PEACH_DATA_ROOT": str(self.root)})
        self.load_config = settings_file.load_config
        self.database = self.config.directory("database") / "ledger.db"
        self.database.parent.mkdir()
        self.state = self.config.directory("state")
        self.state.mkdir()
        patcher = patch.object(update.settings_file, "load_config", return_value=self.config)
        patcher.start(); self.addCleanup(patcher.stop)

    def test_online_install_remembers_a_known_root_only_for_an_empty_default_location(self):
        settings_file.write(self.config)
        config = self.load_config(environ={"PEACH_DATA_ROOT": str(self.root)})
        target = self.root / "app"
        bootstrap = self.root / "default-data"
        with patch.object(update.distribution, "standalone", return_value=True), patch.object(
                update.distribution, "user_data_root", return_value=bootstrap), patch.object(
                update.settings_file, "load_config", side_effect=self.load_config), patch.dict(
                os.environ, {"PEACH_DATA_ROOT": str(self.root)}), patch.object(
                update.sys, "executable", str(target / "Peach.exe")):
            update.write({"target": str(target), "version": update.__version__}, state="ready")
            self.assertFalse(update.remember_installation_data_root(config))
            update.write({"target": str(self.root / "other-app"), "version": update.__version__}, state="installing")
            self.assertFalse(update.remember_installation_data_root(config))
            update.write({"target": str(target), "version": update.__version__}, state="installing")
            self.assertTrue(update.remember_installation_data_root(config))
            self.assertEqual(self.load_config(environ={"PEACH_DATA_ROOT": str(bootstrap)}).data_root, self.root)
            self.assertFalse(update.remember_installation_data_root(config))
            (bootstrap / "state/data-root.txt").unlink()
            settings = bootstrap / "config.toml"
            settings.write_text("[server]\nport = 9123\n", encoding="utf-8")
            self.assertFalse(update.remember_installation_data_root(config))
            self.assertEqual(settings.read_text(encoding="utf-8"), "[server]\nport = 9123\n")

    @unittest.skipUnless(os.name == "nt", "Windows 更新助手")
    def test_tray_reads_update_intent_from_the_selected_data_root_and_passes_it_to_helper(self):
        import threading
        from types import SimpleNamespace
        from dataclasses import replace
        selected = replace(self.config, data_root=self.root / "selected")
        tray = SimpleNamespace(_action_lock=threading.Lock(), exit=Mock())
        with patch.object(update.settings_file, "load_config", return_value=selected), patch.object(
                update.distribution, "standalone", return_value=True), patch.object(update.subprocess, "Popen") as launch:
            update.write({"helper": str(self.root / "helper")}, state="restarting")
            launch.return_value.pid = os.getpid()
            update.poll(tray)
            self.assertEqual(launch.call_args.args[0][2], str(selected.directory("state") / "standalone-update.json"))
            self.assertEqual(launch.call_args.kwargs["env"]["PEACH_DATA_ROOT"], str(selected.data_root))
            tray.exit.assert_called_once_with(reason="standalone-update")
        self.assertEqual(update.read()["state"], "idle")

    def archive(self, names):
        archive = self.root / "package.zip"
        with zipfile.ZipFile(archive, "w") as package:
            for name in names:
                package.writestr(name, "fixture")
        return archive

    def test_zip_requires_a_complete_standalone_layout_and_reports_progress(self):
        archive = self.archive(["Peach/Peach.exe", "Peach/_internal/standalone.txt"])
        progress = Mock()
        root = update.extract(archive, self.root / "extract", progress)
        self.assertTrue((root / "Peach.exe").is_file())
        self.assertEqual(progress.call_args.args, (2, 2))

    def test_zip_rejects_traversal_windows_streams_and_case_collisions(self):
        for name in ("../escape", "Peach/../escape", "C:/escape", "Peach/a:b", "Peach/Peach.exe"):
            with self.subTest(name=name):
                archive = self.archive(["Peach/peach.exe", name])
                with self.assertRaises(ValueError):
                    update.extract(archive, self.root / "extract", Mock())

    def test_stale_progress_is_retryable_and_public_state_hides_paths(self):
        update.write({}, state="downloading", target="private-path", progress=22)
        with patch.object(update.time, "time", return_value=10**12):
            self.assertEqual(update.public()["state"], "error")
        self.assertNotIn("target", update.public())

    def test_restart_requires_ready_and_only_records_intent(self):
        with patch.object(update.distribution, "standalone", return_value=True), patch.object(update.sys, "platform", "win32"):
            with self.assertRaises(ValueError):
                update.request_restart()
            update.write({}, state="ready", version="1.0.0")
            with patch.object(update.subprocess, "Popen") as launch:
                self.assertEqual(update.request_restart()["state"], "restarting")
                launch.assert_not_called()

    def test_source_installs_cannot_start_binary_update(self):
        with patch.object(update.distribution, "standalone", return_value=False):
            with self.assertRaises(ValueError):
                update.start()

    def test_restart_accepts_running_tasks_and_requests_their_pause(self):
        from peach.task_runs import TaskRunStore
        fresh_ledger(self.database.parent)
        store = TaskRunStore(self.database)
        store.start('library-processing', trigger='scheduled')
        update.write({}, state='ready', version='1.0.0')
        with patch.object(update.distribution, 'standalone', return_value=True), patch.object(update.sys, 'platform', 'win32'):
            self.assertEqual(update.request_restart()['state'], 'restarting')
            self.assertTrue(update.update_tasks.is_pausing(self.database))
            with self.assertRaisesRegex(ValueError, '安装更新'):
                store.start('timeline-thumbnails', trigger='manual')
            update.update_tasks.release(self.database, update.read()['task_token'])

    def test_download_prepares_verified_package_without_stopping_the_app(self):
        target = self.root / "installed"; target.mkdir()
        (target / "Peach.exe").write_text("old")
        (target / "unins000.exe").write_text("uninstaller")
        archive = self.archive(["Peach/Peach.exe", "Peach/_internal/standalone.txt"])
        with zipfile.ZipFile(archive, "a") as package:
            package.writestr("Peach/_internal/build-info.json", json.dumps({"version":"1.0.0","commit":None,"built_at":"fixture"}))
        content = archive.read_bytes()
        response = Mock()
        response.iter_bytes.return_value = [content[:10],content[10:]]
        client = Mock()
        client.stream.return_value = nullcontext(response)
        release = dict(state="available", latest_version="1.0.0", asset_size=len(content),
                       asset_digest="sha256:" + hashlib.sha256(content).hexdigest(), asset_url="https://github.com/fixture")
        lock = Mock()
        with patch.object(update.sys,"executable",str(target/"Peach.exe")), patch.object(
                update.release_updates,"check",return_value=release), patch.object(
                update.httpx,"Client",return_value=nullcontext(client)), patch.object(update.subprocess,"Popen") as launch:
            update.prepare({"id":"download-fixture"},lock)
        state = update.read()
        self.assertEqual(state["state"],"ready",state)
        self.assertEqual(state["downloaded"],len(content))
        self.assertTrue((Path(state["helper"])/"Peach.exe").is_file())
        self.assertEqual((Path(state["stage"])/"unins000.exe").read_text(),"uninstaller")
        self.assertEqual((target/"Peach.exe").read_text(),"old")
        launch.assert_not_called()
        lock.release.assert_called_once()

    def test_install_failure_restores_program_directory_and_preserves_data(self):
        target = self.root / "app"; target.mkdir()
        (target / "Peach.exe").write_text("old")
        (target / "_internal").mkdir()
        (target / "_internal" / "standalone.txt").touch()
        transaction = self.root / ".app-update-fixture"; transaction.mkdir()
        stage = transaction / "stage" / "Peach"; stage.mkdir(parents=True)
        (stage / "Peach.exe").write_text("new")
        update.write({"id":"fixture", "target":str(target), "transaction":str(transaction), "stage":str(stage), "version":"1.0.0"}, state="restarting")
        original = update.replace_with_retry
        def replace(source, destination):
            if source == stage:
                raise OSError("occupied")
            original(source, destination)
        with patch("peach.windows_restart.process_alive", return_value=False), patch.object(
                update, "replace_with_retry", side_effect=replace), patch("peach.windows_restart.start_tray") as start:
            self.assertEqual(update.apply(update.state_path(), 999), 1)
        self.assertEqual((target / "Peach.exe").read_text(), "old")
        self.assertEqual(update.public()["state"], "error")
        start.assert_called_once_with(target / "Peach.exe")
        self.assertTrue(self.state.is_dir())

    def test_migration_failure_can_restore_the_sqlite_backup(self):
        with update.closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute("CREATE TABLE fixture(value TEXT)")
            connection.execute("INSERT INTO fixture VALUES ('original')")
        data = {"id":"migration-fixture"}
        def failed_migration(*args, **kwargs):
            with update.closing(sqlite3.connect(self.database)) as connection, connection:
                connection.execute("UPDATE fixture SET value='changed'")
            return Mock(returncode=1)
        with patch("peach.migrations.plan",return_value=([],[object()])), patch.object(
                update.subprocess,"run",side_effect=failed_migration):
            with self.assertRaises(RuntimeError):
                update.migrate_database(self.root,data)
        update.restore_database(data)
        with update.closing(sqlite3.connect(self.database)) as connection:
            self.assertEqual(connection.execute("SELECT value FROM fixture").fetchone()[0],"original")
