Hamamatsu DCAM cameras
======================

To use such a device, installing both, the API and the SDK4 is necessary.
The API is needed to run camera and the SDK4 provides means to control the API via Python.
Both can be downloaded directly from the vendor:

- `DCAM-API Lite for Linux <https://www.hamamatsu.com/eu/en/product/cameras/software/driver-software/dcam-api-lite-for-linux.html>`_
- `DCAM-SDK4 <https://www.hamamatsu.com/eu/en/product/cameras/software/driver-software/dcam-sdk4.html>`_


API
---

The API has to be installed using the included install instructions.
On some linux distributions (e.g. archlinux), you have to run both parts of the installer manually after installing the necessary packages.

.. code::

    # example for usb camera
    # add user to uucp group (possible re-login needed)
    usermod -aG uucp MY_USER
    # install libusb 0.x
    pacman -S libusb-compat
    cd DCAM_API_FOLDER_XXX
    bash api/driver/usb/install.sh
    bash api/runtime/install.sh


SDK4
----
The SDK4 contains (among other things) some Python examples on how to use the API.
Therefore, it includes Python classes which encapsulate the API.
These are located in the subfolder ``dcamsdk4/samples/python``:

- ``dcam.py``
- ``dcamapi4.py``
- ``dcamcon.py``

Clone the `barebone package <https://gitlab.com/atomiq-project/vendor-packages/hamamatsu-dcam-sdk4-python>`_.
Place the three files in question into the subfolder ``src/dcamsdk4/``.
They should reside on the same level as ``__init__.py``.

The structure of the package should resemble::

    .
    ├── pyproject.toml
    ├── README.md
    └── src
        └── dcamsdk4
            ├── dcamapi4.py
            ├── dcamcon.py
            ├── dcam.py
            └── __init__.py

- Open ``dcam.py`` and replace ``from dcamapi4 import *`` by ``from .dcamapi4 import *``.
- Open ``dcamcon.py`` and replace ``from dcam import *`` by ``from .dcam import *``.
- Note the leading dots in both cases.

Finally, in the same Python environment ``herosdevices`` is installed in, install the ``dcamsdk4`` with ``pip``.
