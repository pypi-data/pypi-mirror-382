"""HEROS implementation of the toptica DLC PRO laser driver."""

from heros.helper import log

try:
    from toptica.lasersdk.client import DeviceNotFoundError, DeviceTimeoutError
    from toptica.lasersdk.dlcpro.v3_2_0 import DLCpro, NetworkConnection
except ImportError:
    log.exception("Could not import toptica laser sdk")


DEFAULT_QUERIES = [
    ["set current", "dl.cc.current_set", "mA"],
    ["actual current", "dl.cc.current_act", "mA"],
    ["set temperature", "dl.tc.temp_set", "degC"],
    ["actual temperature", "dl.tc.temp_act", "degC"],
    ["lock Status", "dl.lock.state", ""],
    ["diode ontime", "dl.ontime", "s"],
    ["system health", "system_health", ""],
    ["laser health", "health", ""],
    ["emission status", "emission", ""],
    ["internal PD", "dl.cc.pd", "uA"],
]
"""
default queries
check loop stable parameter values 0:inactive, 1:unstable, 2:stable
check object temperature
syntax
[ [display_name, parameter_id, unit], ]
"""

dlcproorders = (
    "emission_button_enabled",
    "interlock_open",
    "frontkey_locked",
    "emission",
    "system_health",
    "uptime",
    "io",
)
"""Define parameters of the DLCPro and the laser in order to build another function call later"""


class DlcProSource:
    """Reading Toptica DLC Pro parameters via ethernet."""

    def __init__(
        self, ip: str = "127.0.0.1", laser: str = "laser1", queries: list[list[str]] = DEFAULT_QUERIES
    ) -> None:
        self.ip = ip
        self.laser = laser
        self.queries = queries
        self._dlc = None

    def _setup(self) -> None:
        self._connect()

    def _connect(self) -> None:
        """Connect to controller."""
        try:
            con = NetworkConnection(self.ip)
            self._dlc = DLCpro(con).__enter__()
            log.debug("connected to %s", self.ip)
        except (DeviceNotFoundError, DeviceTimeoutError):
            log.error("Could not connect to DLCPro %s via ethernet", self.ip)

    def teardown(self) -> None:
        """Cleanup at the end."""
        try:
            log.debug("closing down connection to %s", self.ip)
            self._dlc.__exit__()
        except AttributeError:
            log.debug("connection to %s was already dead", self.ip)

    @property
    def session(self) -> DLCpro:
        """Return a dlc objects and connect if necessary."""
        if self._dlc is None:
            self._connect()
        return self._dlc

    def _observable_data(self) -> dict:
        """Receiving specified parameters of the Toptica DLC Pro."""
        if self.session is None:
            return None  # TODO: Why is this if and return needed here? type:ignore

        data = {}

        # Connecting to the Toptica DLC Pro via IP address
        try:
            # Building the function call to get the specified parameters
            # Distinguish between parameters for the DLC Pro, the laser and the laserhead
            for description, func_name, unit in self.queries:
                if func_name.startswith(dlcproorders):
                    # Function call for DLCPro parameters
                    option = "self.session." + func_name + ".get"
                else:
                    # Function call for laserhead parameters
                    option = "self.session." + self.laser + "." + func_name + ".get"

                call = eval(option)  # noqa: S307 TODO: Don't use eval.
                value = call()
                data.update({description: (value, unit)})

        except Exception:  # noqa: BLE001
            # something went wrong, reconnect
            log.exception("something went wrong")
            self._dlc = None

        return data
