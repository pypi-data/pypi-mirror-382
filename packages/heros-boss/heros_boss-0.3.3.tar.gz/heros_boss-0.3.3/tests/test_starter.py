from heros import RemoteHERO
from boss.starter import run
import subprocess
import time


def test_autostart(default_starter_env, cleanup):
    boss_processes = [
        subprocess.Popen(
                [
                    "python",
                    "-m",
                    "boss.starter",
                    "--no-autostart",
                    "-e",
                    "BOSS1",
                    "--expose",
                    "--log=debug",
                    "--name=test_boss",
                ],
            ),
        subprocess.Popen(
                [
                    "python",
                    "-m",
                    "boss.starter",
                    "-e",
                    "BOSS2",
                    "--expose",
                    "--log=debug",
                    "--name=test_boss2",
                ],
            ),
    ]
    time.sleep(1)
    boss = RemoteHERO("test_boss")
    cleanup["boss"].append([boss_processes[0],boss])
    assert boss.status()["test_dev"]["status"] == "stopped"

    boss2 = RemoteHERO("test_boss2")
    cleanup["boss"].append([boss_processes[1],boss2])
    assert boss2.status()["test_dev2"]["status"] == "running"

def test_realm_and_tags(default_starter_env, cleanup):
    boss_processes = [
        subprocess.Popen(
                [
                    "python",
                    "-m",
                    "boss.starter",
                    "-e",
                    "BOSS1",
                    "--expose",
                    "--log=debug",
                    "--name=test_boss_realm",
                    "--realm=test_realm",
                ],
            ),
    ]
    time.sleep(1)
    boss = RemoteHERO("test_boss_realm", realm="test_realm")
    cleanup["boss"].append([boss_processes[0],boss])

    hero = RemoteHERO("test_dev", realm="test_realm")
    cleanup["heros"].append(hero)

    assert "BOSS: test_boss_realm" in hero._hero_tags
    assert "test_tag" in hero._hero_tags

