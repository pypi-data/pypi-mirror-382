import pytest
import os
from unittest import mock
import json
import time
from heros.zenoh import session_manager as default_session_manager


@pytest.fixture()
def default_starter_env():
    boss_config = json.dumps({
        "_id": "test_dev",
           "classname": "boss.dummies.Dummy",
           "arguments": {
           },
           "tags": ["test_tag"],
       })
    boss_config2 = json.dumps({
        "_id": "test_dev2",
           "classname": "boss.dummies.Dummy",
           "arguments": {
           }
       })
    with mock.patch.dict(os.environ, {"BOSS1": boss_config, "BOSS2": boss_config2}):
        yield

@pytest.fixture(scope="session")
def cleanup():
    cleanups = {"boss": [], "heros":[]}
    yield cleanups
    for hero in cleanups["heros"]:
        hero._destroy_hero()
    for boss_process in cleanups["boss"]:
        for hero in boss_process[1].status():
            boss_process[1].stop_hero(hero)
        boss_process[1]._destroy_hero()
        boss_process[0].terminate()
    for boss_process in cleanups["boss"]:
        while boss_process[0].poll() is None:
            time.sleep(0.1)
    del cleanups
    default_session_manager.force_close()
