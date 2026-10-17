import csv
import json
import sqlite3
import tempfile
import unittest
import zipfile
from contextlib import closing
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
import pathlib
from urllib.parse import quote
from unittest import mock

from peach import taste_history
from peach.taste_history import (
    HistorySource,
    analyze_history,
    build_taste_dashboard,
    discover_history_sources,
    import_history_exports,
    refresh_history,
    refresh_takeout_history,
)


class TasteHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _firefox_db(self, path: Path) -> None:
        path.parent.mkdir(parents=True)
        with closing(sqlite3.connect(path)) as db:
            db.executescript(
                "CREATE TABLE moz_places(id INTEGER PRIMARY KEY, url TEXT, title TEXT, "
                "description TEXT, preview_image_url TEXT);"
                "CREATE TABLE moz_historyvisits(id INTEGER PRIMARY KEY, place_id INTEGER, visit_date INTEGER);"
            )
            db.execute("INSERT INTO moz_places VALUES (1, ?, ?, NULL, NULL)", ("https://rule34.xxx/search?tags=feet+cosplay", "secret"))
            db.execute("INSERT INTO moz_historyvisits VALUES (1, 1, 1700000000000000)")
            db.commit()

    def _chrome_db(self, path: Path) -> None:
        path.parent.mkdir(parents=True)
        with closing(sqlite3.connect(path)) as db:
            db.executescript(
                "CREATE TABLE urls(id INTEGER PRIMARY KEY, url TEXT, title TEXT);"
                "CREATE TABLE visits(id INTEGER PRIMARY KEY, url INTEGER, visit_time INTEGER, visit_duration INTEGER);"
            )
            db.execute("INSERT INTO urls VALUES (1, ?, ?)", ("https://onlyfans.com/creator_name", "private title"))
            db.execute("INSERT INTO visits VALUES (2, 1, 13344473600000000, 0)")
            db.commit()

    def _safari_db(self, path: Path) -> None:
        path.parent.mkdir(parents=True)
        with closing(sqlite3.connect(path)) as db:
            db.executescript(
                "CREATE TABLE history_items(id INTEGER PRIMARY KEY, url TEXT);"
                "CREATE TABLE history_visits(id INTEGER PRIMARY KEY, history_item INTEGER, visit_time REAL, title TEXT);"
            )
            db.execute("INSERT INTO history_items VALUES (1, ?)", ("https://rule34video.com/models/alice/",))
            db.execute("INSERT INTO history_visits VALUES (3, 1, 700000000, 'hidden')")
            db.commit()

    def _takeout_zip(self, path: Path) -> None:
        overlap_url = "https://onlyfans.com/takeout_creator"
        unique_url = "https://rule34.xxx/index.php?page=post&s=list&tags=feet"
        history = {
            "Browser History": [
                {"url": overlap_url, "title": "private takeout title", "time_usec": 1700000000123456},
                {"url": unique_url, "title": "another private title", "time_usec": 1700000100000000},
            ]
        }
        activity_rows = [
            (overlap_url, 1700000000, "private activity title"),
            ("https://fansly.com/activity_only", 1700000200, "activity only title"),
        ]
        cards: list[str] = []
        for url, timestamp, title in activity_rows:
            local = datetime.fromtimestamp(timestamp, UTC).astimezone(timezone(timedelta(hours=8)))
            hour = (local.hour - 1) % 12 + 1
            date = f"{local:%b} {local.day}, {local.year}, {hour}:{local:%M:%S} {local:%p} HKT"
            wrapped = f"https://www.google.com/url?q={quote(url, safe='')}"
            cards.append(
                '<div class="outer-cell"><div><div>Visited&nbsp;'
                f'<a href="{wrapped}">{title}</a><br>{date}<br>Products:<br>Chrome'
                "</div></div></div>"
            )
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("Takeout/Chrome/History.json", json.dumps(history))
            archive.writestr("Takeout/My Activity/Chrome/MyActivity.html", "<html>" + "".join(cards) + "</html>")
            archive.writestr(
                "Takeout/My Activity/Search/MyActivity.html",
                '<html><div class="outer-cell"><div><div>Searched for&nbsp;'
                '<a href="https://www.google.com/search?q=test">private search</a><br>'
                "Nov 15, 2023, 9:18:20 PM HKT<br>Products:<br>Search"
                "</div></div></div></html>",
            )

    def test_discovers_windows_firefox_and_chrome_profiles(self):
        roaming = self.root / "Roaming"
        local = self.root / "Local"
        self._firefox_db(roaming / "Mozilla" / "Firefox" / "Profiles" / "default" / "places.sqlite")
        self._chrome_db(local / "Google" / "Chrome" / "User Data" / "Default" / "History")
        sources = discover_history_sources(
            home=self.root, appdata=roaming, localappdata=local, platform_name="windows"
        )
        self.assertEqual([source.browser for source in sources], ["chrome", "firefox"])

    def test_discovers_macos_zen_safari_firefox_and_chrome_profiles(self):
        support = self.root / "Library" / "Application Support"
        paths = [
            support / "Firefox" / "Profiles" / "firefox" / "places.sqlite",
            support / "zen" / "Profiles" / "zen" / "places.sqlite",
            support / "Google" / "Chrome" / "Default" / "History",
            self.root / "Library" / "Safari" / "History.db",
        ]
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        sources = discover_history_sources(home=self.root, platform_name="macos")
        self.assertEqual([source.browser for source in sources], ["chrome", "firefox", "safari", "zen"])

    def test_the_history_store_has_one_entry_point(self):
        """打开私有历史库的前导只许有一份。

        它此前在三个入口里各写了一份。共享的不只是形状：`_prepare_store` 漏掉一次，
        写入就撞上不存在的表；而 host 参与 source_key，三处算法必须一致，否则同一台
        机器的历史会被记成两个来源。

        `remove_history_source` 刻意不走它——库不存在时那条路径要返回 0，而不是顺手
        把库建出来。
        """
        source = pathlib.Path(taste_history.__file__).read_text(encoding="utf-8")
        self.assertEqual(source.count("store_path.parent.mkdir(parents=True, exist_ok=True)"), 1,
                         "又有入口自己写了前导，请改用 _open_history_store")

    def test_refresh_is_incremental_and_report_omits_urls_and_titles(self):
        firefox = self.root / "firefox" / "places.sqlite"
        chrome = self.root / "chrome" / "History"
        safari = self.root / "Safari" / "History.db"
        self._firefox_db(firefox)
        self._chrome_db(chrome)
        self._safari_db(safari)
        sources = [
            HistorySource("firefox", "default", firefox),
            HistorySource("chrome", "Default", chrome),
            HistorySource("safari", "iCloud", safari),
        ]
        store = self.root / "sources" / "history.sqlite"
        updates = []
        first = refresh_history(sources, store, host="test-host", progress=lambda **state: updates.append(state))
        self.assertEqual(updates[-1]["checked"], first[-1]["visits"])
        self.assertIsNone(updates[-1]["total"])
        self.assertNotIn("secret", str(updates))
        second = refresh_history(sources, store, host="test-host")
        self.assertEqual(sum(item["added"] for item in first), 3)
        self.assertEqual(sum(item["added"] for item in second), 0)

        output = self.root / "review"
        result = analyze_history(store, output, progress=lambda **state: updates.append(state))
        measured = [state for state in updates if state["stage"] == "analyzing"]
        self.assertEqual(measured[0]["checked"], 0)
        self.assertEqual(measured[-1]["checked"], result["visits"])
        self.assertEqual(measured[-1]["total"], result["visits"])
        self.assertEqual(updates[-1]["stage"], "reporting")
        report = Path(result["report"]).read_text(encoding="utf-8")
        self.assertIn("足系", report)
        self.assertIn("cosplay", report)
        self.assertIn("alice", report)
        self.assertNotIn("https://", report)
        self.assertNotIn("secret", report)
        self.assertNotIn("private title", report)
        with Path(result["creators"]).open(encoding="utf-8-sig", newline="") as handle:
            creators = {row["candidate"] for row in csv.DictReader(handle)}
        self.assertEqual(creators, {"alice", "creator_name"})

    def test_takeout_import_recovers_activity_and_deduplicates_sources(self):
        archive = self.root / "takeout.zip"
        self._takeout_zip(archive)
        store = self.root / "sources" / "history.sqlite"

        first = refresh_takeout_history([archive], store, host="test-host")
        second = refresh_takeout_history([archive], store, host="test-host")

        self.assertEqual(
            [(item["profile"], item["visits"], item["added"]) for item in first],
            [
                ("Takeout Browser History", 2, 2),
                ("Google My Activity - Chrome", 2, 1),
                ("Google My Activity - Search", 1, 1),
            ],
        )
        self.assertEqual(sum(item["added"] for item in second), 0)
        with closing(sqlite3.connect(store)) as db:
            rows = db.execute("SELECT url, title FROM history_visit ORDER BY visited_at").fetchall()
        self.assertEqual(len(rows), 4)
        self.assertTrue(all("google.com/url" not in url for url, _title in rows))
        self.assertIn(("https://fansly.com/activity_only", "activity only title"), rows)

        result = analyze_history(store, self.root / "review")
        report = Path(result["report"]).read_text(encoding="utf-8")
        self.assertNotIn("https://", report)
        self.assertNotIn("private takeout title", report)

    def test_browserexport_json_and_peach_behavior_build_one_private_dashboard(self):
        exported = self.root / "history.json"
        exported.write_text(json.dumps([
            {
                "url": (
                    "https://rule34.xxx/index.php?page=post&s=list&tags="
                    "feet+-gay+-ai_generated+detroit_become_human+big_breasts"
                ),
                "dt": 1_700_000_000,
                "metadata": {"title": "private", "description": None,
                             "preview_image": None, "duration": None},
            },
            {
                "url": "https://onlyfans.com/alice",
                "dt": 1_700_000_100,
                "metadata": None,
            },
        ]), encoding="utf-8")
        store = self.root / "sources" / "history.sqlite"
        imported = import_history_exports([exported], store, host="test-host")
        self.assertEqual(imported[0]["added"], 2)

        ledger = self.root / "ledger.db"
        with closing(sqlite3.connect(ledger)) as db:
            db.row_factory = sqlite3.Row
            db.executescript(
                "CREATE TABLE asset(id INTEGER PRIMARY KEY,creator TEXT,studio TEXT,play_count INTEGER,"
                "play_seconds REAL,o_count INTEGER,rating INTEGER,feedback TEXT,last_played REAL);"
                "CREATE TABLE asset_preference(profile_id TEXT,asset_id INTEGER,liked INTEGER);"
                "CREATE TABLE entity(id INTEGER PRIMARY KEY,kind TEXT,canonical_name TEXT,normalized_name TEXT);"
                "CREATE TABLE asset_entity(asset_id INTEGER,entity_id INTEGER);"
            )
            db.execute("INSERT INTO asset VALUES(1,'Alice','Studio',2,600,1,80,NULL,1700000200)")
            db.execute("INSERT INTO asset_preference VALUES('local-default',1,1)")
            db.execute("INSERT INTO entity VALUES(1,'tag','feet','feet')")
            db.execute("INSERT INTO entity VALUES(2,'creator','Alice','alice')")
            db.execute("INSERT INTO entity VALUES(3,'tag','中片-10分内','中片-10分内')")
            db.execute("INSERT INTO entity VALUES(4,'performer','Bob','bob')")
            db.execute("INSERT INTO entity VALUES(5,'tag','游戏同人','游戏同人')")
            db.execute("INSERT INTO entity VALUES(6,'tag','恋足','恋足')")
            db.execute("INSERT INTO asset_entity VALUES(1,1)")
            db.execute("INSERT INTO asset_entity VALUES(1,2)")
            db.execute("INSERT INTO asset_entity VALUES(1,3)")
            db.execute("INSERT INTO asset_entity VALUES(1,4)")
            db.execute("INSERT INTO asset VALUES(2,NULL,NULL,0,0,0,0,NULL,NULL)")
            db.execute("INSERT INTO asset VALUES(3,NULL,NULL,0,0,0,0,NULL,NULL)")
            db.execute("INSERT INTO asset_entity VALUES(2,5)")
            db.execute("INSERT INTO asset_entity VALUES(3,6)")
            db.commit()
            dashboard = build_taste_dashboard(store, db)
            future = build_taste_dashboard(store, db, since="2099-01-01T00:00:00+00:00")
            history = taste_history._history_dashboard_evidence(store, None)
            history["domains"].update({f"popular-{index}.example": 1000 for index in range(7)})
            with mock.patch.object(taste_history, "_history_dashboard_evidence", return_value=history):
                unrelated_traffic = build_taste_dashboard(store, db)
            db.execute("UPDATE asset SET feedback='dislike' WHERE id=1")
            discovery_taste = build_taste_dashboard(store, db, exclude_disliked=True)

        self.assertEqual(dashboard["summary"]["history_visits"], 2)
        self.assertEqual(dashboard["activity"]["days"], [{"date": "2023-11-15", "count": 2}])
        self.assertEqual(dashboard["activity"]["hours"], [{"weekday": 2, "hour": 6, "count": 2}])
        self.assertEqual(dashboard["creator_flows"], [{"source": "onlyfans.com", "target": "alice", "value": 1}])
        self.assertEqual(unrelated_traffic["creator_flows"], dashboard["creator_flows"])
        self.assertEqual(future["activity"]["days"], [])
        self.assertEqual(future["creator_flows"], [])
        self.assertEqual(future["rankings"]["browser_categories"], [])
        self.assertGreater(dashboard["summary"]["history_sources"], 0)
        self.assertEqual(future["summary"]["history_visits"], 0)
        self.assertEqual(future["summary"]["history_sources"], dashboard["summary"]["history_sources"])
        self.assertEqual(dashboard["summary"]["peach_items"], 1)
        feet = dashboard["rankings"]["tags"][0]
        self.assertEqual(feet["name"], "feet")
        self.assertEqual(feet["web_visits"], 1)
        self.assertEqual(feet["peach_items"], 1)
        alice = dashboard["rankings"]["creators"][0]
        self.assertEqual(alice["evidence"], ["浏览记录", "Peach"])
        self.assertEqual(alice["entity_id"], 2)
        self.assertEqual(dashboard["rankings"]["browser_creators"][0]["name"], "Alice")
        self.assertEqual(dashboard["rankings"]["browser_creators"][0]["source_domain"], "onlyfans.com")
        self.assertEqual(dashboard["rankings"]["peach_creators"][0]["name"], "Alice")
        self.assertEqual(dashboard["rankings"]["peach_performers"][0]["entity_id"], 4)
        self.assertEqual(dashboard["rankings"]["peach_studios"][0]["name"], "Studio")
        self.assertTrue(all(float(row["score"]) == 0 for row in discovery_taste["rankings"]["peach_performers"]))
        self.assertEqual(discovery_taste["summary"]["disliked"], 1)
        browser_tags = {row["name"] for row in dashboard["rankings"]["browser_tags"]}
        self.assertIn("detroit_become_human", browser_tags)
        self.assertIn("big_breasts", browser_tags)
        self.assertTrue({"ai", "generated", "ai_generated", "gay"}.isdisjoint(browser_tags))
        categories = {row["name"] for row in dashboard["rankings"]["categories"]}
        self.assertIn("游戏同人", categories)
        self.assertIn("乳系", categories)
        self.assertNotIn("中片-10分内", json.dumps(dashboard, ensure_ascii=False))
        self.assertNotIn("negative_tags", dashboard["rankings"])
        self.assertTrue(dashboard["privacy"]["dislikes_do_not_downrank_tags"])
        self.assertNotIn("url", json.dumps(dashboard).casefold())
        analysis = dashboard["analysis"]
        self.assertEqual(analysis["confidence"]["level"], "early")
        self.assertTrue(any("足系" in row["text"] for row in analysis["points"]))
        explore_tags = {row["tag"] for row in analysis["explore"]}
        self.assertTrue({"游戏同人", "恋足"}.issubset(explore_tags))
        self.assertTrue(all(row["items"] > 0 for row in analysis["explore"]))
        self.assertIn("不合口味", analysis["next_steps"][-1]["detail"])

    def test_history_is_parsed_once_per_store_version(self):
        def export(name, url, moment):
            path = self.root / name
            path.write_text(json.dumps([{"url": url, "dt": moment, "metadata": None}]), encoding="utf-8")
            return path

        store = self.root / "sources" / "history.sqlite"
        import_history_exports([export("a.json", "https://onlyfans.com/alice", 1_700_000_000)],
                               store, host="test-host")
        reads = []
        original = taste_history._read_history_rows

        def counted(path):
            reads.append(path)
            return original(path)

        with mock.patch.object(taste_history, "_read_history_rows", side_effect=counted):
            first = taste_history._history_dashboard_evidence(store, None)
            recent = taste_history._history_dashboard_evidence(store, "2099-01-01T00:00:00+00:00")
            self.assertEqual(len(reads), 1)
            self.assertEqual(first["visits"], 1)
            self.assertEqual(recent["visits"], 0)
            self.assertEqual(recent["sources"], first["sources"])

            import_history_exports([export("b.json", "https://fansly.com/bob", 1_700_000_100)],
                                   store, host="test-host")
            second = taste_history._history_dashboard_evidence(store, None)
        self.assertEqual(len(reads), 2)
        self.assertEqual(second["visits"], 2)
        self.assertEqual(set(second["creators"]), {"alice", "bob"})
        self.assertEqual(second["range_end"], datetime.fromtimestamp(1_700_000_100, UTC).isoformat())


if __name__ == "__main__":
    unittest.main()
