import pytest
from src.heros.heros import LocalHERO, RemoteHERO
from src.heros.event import event
from src.heros.inspect import force_remote, local_only
import time


@pytest.fixture(scope="session")
def local_hero_device():
    class TestDevice(LocalHERO):
        int_var: int = 3

        def my_method(self, str_arg: str) -> str:
            return str_arg

        def complex_signature(self, pos_1: int, /, pos_2: int, *args, kw: int = 1, **kwargs) -> tuple:
            return pos_1, pos_2, args, kw, kwargs

        def weird_name_signature(self, args: int, kwargs: str) -> tuple:
            return args, kwargs

        @event
        def my_event(self, str_arg: str) -> str:
            return str_arg

        def _local_only(self):
            return True

        @local_only
        def forced_local(self):
            return True

        @force_remote
        def _forced_remote(self):
            return True

    dev = TestDevice("test_hero")
    yield dev
    dev._destroy_hero()
    time.sleep(0.3)
    dev._session_manager.force_close()


@pytest.fixture(scope="session")
def remote_hero_device():
    hero = RemoteHERO("test_hero")
    yield hero
    hero._destroy_hero()
    time.sleep(0.3)
    hero._session_manager.force_close()


@pytest.fixture()
def local_method(mocker):
    class Foo:
        def echo(self, str_arg: str) -> str:
            return str_arg

    foo = Foo()
    spy = mocker.spy(foo, "echo")
    return spy
