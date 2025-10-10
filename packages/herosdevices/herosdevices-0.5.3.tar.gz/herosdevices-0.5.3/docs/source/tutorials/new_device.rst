Building a Custom Arduino Driver for DHT11 Sensors
==================================================

Introduction
------------

This tutorial demonstrates how to create a custom device driver for an Arduino
board with two DHT11 sensors attached to it. The driver will communicate over a
serial connection and assumes that your Arduino replies to commands like ``t0``,
``t1``, ``h0``, and ``h1`` with the according sensor readings.

Where to Put the Driver?
------------------------
This does not really matter as long as it accessible from your
`boss <https://gitlab.com/atomiq-project/boss>`_ installation.
The easiest way is to download the herosdevices git repository and create your own branch

.. code-block:: bash

   git clone https://gitlab.com/atomiq-project/herosdevices.git
   cd herosdevices
   git checkout -b temperature_arduino


.. note::

   If you want to contribute your device driver upstream to the community it
   makes sense to create your own fork of the herostools repository. Learn more
   about forks `here <https://docs.gitlab.com/user/project/repository/forking_workflow/>`_.

Next, open the file :code:`src/herosdevices/hardware/arduino.py` in your favourite text editor.

Implementation
--------------

We start by importing the :py:class:`herosdevices.core.templates.SerialDeviceTemplate` template, which provides the foundation for serial communication and let our class inherit from it.

.. code-block:: python
    :linenos:

    from herosdevices.core.templates import SerialDeviceTemplate

    class TempArduino(SerialDeviceTemplate):
        """
        An Arduino with two DHT11 humidity/temperature sensors attached to it.
        """
        pass


-----------------

Next, we add an ``__init__`` method to initialize the serial connection. Here
we set up the serial connection with the correct baud rate and line
termination. The explicit values depend on your Arduino implementation but the
ones used here are typically the default values. Arguments of the ``__init__``
function (here for example ``address``) are then latter defined in a :doc:`JSON <boss:json>`
string which is passed to the device by `boss <https://gitlab.com/atomiq-project/boss>`_ on startup.

.. code-block:: python
    :linenos:

    def __init__(self, address: str, *args, **kwargs):
        super().__init__(address, baudrate=9600, line_termination=b"\n", *args, **kwargs)

-----------------

Now, we define the attributes for each sensor using :py:class:`herosdevices.core.DeviceCommandQuantity`. These attributes represent the commands to get temperature and humidity readings from the Arduino.

.. code-block:: python
    :linenos:

    from herosdevices.core import DeviceCommandQuantity

    class TempArduino(SerialDeviceTemplate):
        """
        An Arduino with two DHT11 humidity/temperature sensors attached to it.
        """
        temperature_0 = DeviceCommandQuantity(
            command_get="t0\r\n",
            dtype=float,
            unit="°C",
        )
        temperature_1 = DeviceCommandQuantity(
            command_get="t1\r\n",
            dtype=float,
            unit="°C",
        )
        humidity_0 = DeviceCommandQuantity(
            command_get="h0\r\n",
            dtype=float,
            unit="%",
        )
        humidity_1 = DeviceCommandQuantity(
            command_get="h1\r\n",
            dtype=float,
            unit="%",
        )

Each ``DeviceCommandQuantity`` defines a command to send to the Arduino (e.g., ``"t0\n"`` for the first temperature sensor), the expected data type (``float``) and the unit of measurement.

.. note::

  The :py:class:`herosdevices.core.DeviceCommandQuantity` supports more complex casting and extraction of values from
  the values returned by the Arduino. Refer to the documentation of :py:class:`herosdevices.core.DeviceCommandQuantity` for more details.

-----------------

This works for two sensors but for more sensors defining each sensor separately is kind of ugly.
To do this in a more readable and maintainable way we can attach to the ``__new__`` method which is called to create
an instance of the class.

.. code-block:: python
    :linenos:

    from herosdevices.core import DeviceCommandQuantity
    from herosdevices.helper import add_class_descriptor

        def __new__(cls, *args, **kwargs):
            for i_channel in range(2):
                name_str_t = f"temperature_{i_channel}"
                name_str_h = f"humidity_{i_channel}"
                add_class_descriptor(
                    cls, name_str_t, DeviceCommandQuantity(command_get=f"t{i_channel}", dtype=float, unit="°C")
                )
                add_class_descriptor(
                    cls, name_str_h, DeviceCommandQuantity(command_get=f"t{i_channel}", dtype=float, unit="%")
                )
            return super().__new__(cls)


The imported `add_class_descriptor` function takes care that the attributes are added in a way that they are
directly visible to HEROS and are accessible from remote (e.g. with ``obj.temperature_0`` from the
`HERO Monitor <https://gitlab.com/atomiq-project/hero-monitor>`_.

----------------

Finally, we can add a ``_observale_data`` method so the class can be used for automatic observable data recording in combination
with the :external+herostools:py:class:`herostools.actor.statemachine.HERODatasourceStateMachine`.

.. code-block:: python
    :linenos:

        def _observable_data(self):
            return {
                "temperature_0": (self.temperature_0, "°C"),
                "temperature_1": (self.temperature_1, "°C"),
                "humidity_0": (self.humidity_0, "%"),
                "humidity_1": (self.humidity_1, "%"),
            }

Again this feels clumsy for more than one sensor. An easy way to make it more
maintainable and also add some configuratability in the case you not always
want to log everything is to introduce a dictionary ``observables`` which is
then used to determine which observables are collected. Also one can define
which observables are logged by default in the ``__new__`` method.

The complete file including the observables mechanics looks now as follows:

.. code-block:: python
    :linenos:

    from herosdevices.core.templates import SerialDeviceTemplate
    from herosdevices.core import DeviceCommandQuantity
    from herosdevices.helper import add_class_descriptor

    class TempArduino(SerialDeviceTemplate):
        """
        An Arduino with two DHT11 humidity/temperature sensors attached to it.
        """

        observables: dict

        def __new__(cls, *args, **kwargs):
            for i_channel in range(2):
                name_str_t = f"temperature_{i_channel}"
                name_str_h = f"humidity_{i_channel}"
                add_class_descriptor(
                    cls, name_str_t,
                    DeviceCommandQuantity(command_get=f"t{i_channel}", dtype=float, unit="°C")
                )
                add_class_descriptor(
                    cls, name_str_h,
                    DeviceCommandQuantity(command_get=f"t{i_channel}", dtype=float, unit="%")
                )
                cls.default_observables[name_str_t] = {"name": name_str_t, "unit": "°C"}
                cls.default_observables[name_str_h] = {"name": name_str_h, "unit": "%"}
            return super().__new__(cls)

        def __init__(self, address: str, *args, observables: dict | None,  **kwargs):
            self.observables = observables if observables is not None else self.default_observables
            super().__init__(address, baudrate=9600, line_termination=b"\n", *args, **kwargs)

        def _observable_data(self):
            data = {}
            for attr, description in self.observables.items():
                data[description["name"]] = (getattr(self, attr), description["unit"])
            return data

Installation and Configuration
-------------------------------

To start the driver as a HERO, the easiest way is to use boss `boss <https://gitlab.com/atomiq-project/boss>`_.
The following :doc:`JSON <boss:json>` code creates and instance of the driver, including the observable logging functionality.
Put that code into a file ``arduino.json`` somewhere to your liking.

.. note::

   For production use, we recommend setting up a :doc:`CouchDB <boss:couchdb>` to organise your JSON files
   to be accessible from everywhere in the network.


.. code-block:: json
    :linenos:

    {
      "_id": "temp-arduino",
      "classname": "herosdevices.hardware.arduino.TempArduino",
      "arguments": {
        "address": "/dev/ttyUSB0"
      },
      "datasource": {
        "async": false,
        "interval": 300
      }
    }

This configuration queries the Arduino every 300 seconds and emits temperature/humidity data via the ``observable_data`` event.
For more information on data handling with datasources check the
:external+heros:py:class:`heros.datasource.datasource.LocalDatasourceHERO` documentation.

Now install boss in a python virtual environment and execute the following command within the virtual environment
to start the arduino HERO

.. code-block:: bash

   python -m boss.starter -u file:./arduino.json

You should now see something like the following output in the command line

.. code-block:: bash

   2025-09-09 14:20:49,566 boss: Reading device(s) from ['file:./arduino.json']
   2025-09-09 14:20:49,566 boss: refreshing HERO source file:./arduino.json
   2025-09-09 14:20:49,623 boss: creating HERO with name temp-arduino from class herosdevices.hardware.arduino.TempArduino failed: No module named 'herosdevices.hardware.arduino'
   2025-09-09 14:20:49,623 boss: Starting BOSS


You can now also see your device "temp-arduino" in `HERO Monitor <https://gitlab.com/atomiq-project/hero-monitor>`_
and read out temperatures and humidities from there.


