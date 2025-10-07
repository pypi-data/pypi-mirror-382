import pytest
from src.heros.zenoh import ZenohSessionManager
from src.heros.heros import LocalHERO
import time


def test_create_destroy():
    manager = ZenohSessionManager()
    with LocalHERO("test_hero_with_manager", session_manager=manager) as hero:
        assert manager._referrers == [hero]
        manager.release_session(hero)
    time.sleep(0.2)
    assert manager._referrers == []
    manager.force_close()


def test_method(local_hero_device, remote_hero_device):
    assert remote_hero_device.my_method("test str") == local_hero_device.my_method("test str")


def test_complex_signature(local_hero_device, remote_hero_device):
    res = remote_hero_device.complex_signature(200, 100, 1, 2, kw2="str", kw3="test", kw=5)
    assert res == [200, 100, [1, 2], 5, {"kw2": "str", "kw3": "test"}]
    res = remote_hero_device.weird_name_signature(200, kwargs="weird")
    assert res == [200, "weird"]


def test_arg(local_hero_device, remote_hero_device):
    assert remote_hero_device.int_var == local_hero_device.int_var
    remote_hero_device.int_var = 10
    assert remote_hero_device.int_var == local_hero_device.int_var


def test_force_remote_local(remote_hero_device, local_hero_device):
    with pytest.raises(AttributeError):
        remote_hero_device.forced_local()
    with pytest.raises(AttributeError):
        remote_hero_device._local_only()
    assert local_hero_device._local_only()
    assert remote_hero_device._forced_remote()
