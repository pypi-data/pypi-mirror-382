import asyncio

from heros import LocalHERO, EventObserver
from heros.event import event
from heros.inspect import local_only
from heros.helper import log
from .types import DatasourceReturnSet, DatasourceReturnValue
from .observables import ObservableProcessor


class LocalDatasourceHERO(LocalHERO):
    """
    A datasource is a HERO that can provide information on a standardized interface.
    This interface is the event `observable_data`. Instances in the zenoh network interested in the data provided
    by data sources can simply subscribe to the key expression `@objects/realm/*/observable_data` or use
    the :class:`DatasourceObserver`.

    To make your class a LocalDatasourceHERO make it inherit this class.
    This class is meant for datasources that create asynchronous events on their own. When processing such an event
    call `observable_data` to publish the data from this datasource.

    Args:
        name: name/identifier under which the object is available. Make sure this name is unique in the realm.
        realm: realm the HERO should exist in. default is "heros"
    """

    def __init__(self, *args, observables: dict | None = None, **kwargs):
        observables = {} if observables is None else observables
        LocalHERO.__init__(self, *args, **kwargs)
        self.observable_processor = ObservableProcessor(observables)

    def _process_data(self, data):
        return self.observable_processor(DatasourceReturnSet.from_data(data))

    @event
    def observable_data(self, data):
        return self._process_data(data)


class DatasourceObserver(EventObserver):
    """
    A class that can observe and handle the data emitted by one or more datasource HEROs.
    In particular, this class provides an efficient way to listen to the data emitted by all datasource HEROs in
    the realm. By not instantiating the HEROs themselves but just subscribing to the topics for the datasource, this
    reduces the pressure on the backing zenoh network. If, however, only the data of a few HEROs should be observed,
    it might make more sense to just instantiate the according RemoteHEROs and connect a callback to their `observable_data`
    signal.

    Args:
        object_selector: selector to specify which objects to observe. This becomes part of a zenoh selector and thus
        can be anything that makes sense in the selector. Defaults to * to observe all HEROs in the realm.
    """

    def __init__(self, object_selector: str = "*", *args, **kwargs):
        EventObserver.__init__(self, object_selector=object_selector, event_name="observable_data", *args, **kwargs)

    def _handle_event(self, key_expr: str, data):
        try:
            data = DatasourceReturnSet([DatasourceReturnValue(**d) for d in data])
            EventObserver._handle_event(self, key_expr=key_expr, data=data)
        except Exception as e:
            log.warn(f"Could not convert data {data} into DatasourceReturnSet: {e}")

    def register_observable_data_callback(self, func: callable):
        """
        Register a callback that should be called on observable_data.
        This method passes the function to `EventObserver.register_callback`

        Args:
            func: function to call on observable_data.
        """
        self.register_callback(func)


class PolledLocalDatasourceHERO(LocalDatasourceHERO):
    """
    This local HERO periodically triggers the event "observable_data" to poll and publish data.
    This class is meant for datasources that do not generate events on their own an thus should be polled
    on a periodical basis.

    To make your class a PolledLocalDatasourceHERO make it inherit this class an implement the method `_observable_data`.
    The method will get called periodically and the return value will be published as an event.

    Note:
        The periodic calling is realized via asyncio and will thus only work if the asyncio mainloop is
        started.

    Args:
        name: name/identifier under which the object is available. Make sure this name is unique in the realm.
        realm: realm the HERO should exist in. default is "heros"
        interval: time interval in seconds between consecutive calls of `observable_data` event
    """

    def __init__(self, *args, loop, interval: float = 5, **kwargs):
        LocalDatasourceHERO.__init__(self, *args, **kwargs)
        self.datasource_interval = interval
        self._loop = loop
        self._stop_loop = asyncio.Event()
        self._loop_task = self._loop.call_soon_threadsafe(asyncio.create_task, self._trigger_datasource())

    async def _trigger_datasource(self):
        while not self._stop_loop.is_set():
            self.observable_data()
            try:
                await asyncio.wait_for(self._stop_loop.wait(), self.datasource_interval)
            except TimeoutError:
                # we want that, ignore
                pass

    @local_only
    def _destroy_hero(self):
        self._loop.call_soon_threadsafe(self._stop_loop.set)
        super()._destroy_hero()

    @event
    def observable_data(self):
        return self._process_data(self._observable_data())

    def _observable_data(self):
        msg = (
            f"Implement _observable_data() in a subclass of PolledLocalDatasourceHERO: Not present in HERO "
            f"'{self._name}' of class {self.__class__.__name__.strip('_HERO')}"
        )
        raise NotImplementedError(msg)
