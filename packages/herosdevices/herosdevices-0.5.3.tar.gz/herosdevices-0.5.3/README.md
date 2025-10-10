<h1 align="center">
<img src="https://gitlab.com/atomiq-project/herosdevices/-/raw/main/docs/_static/logo.svg" width="150">
</h1>

# HEROS Devices
This repository contains python representations (think drivers) of frequently used lab equipment. While these drivers
can be perfectly used also locally on the system attached to the lab equipment, the real advantage arises, when the
created python object is made available in the network via [HEROS](https://gitlab.com/atomiq-project/heros).

The drivers in this repository sit in the hardware submodule and are arranged in submodules corresponding the vendor
name of the device.

## Howto Use

### Standalone
The hardware control code in this repository is developed as stand-alone code. That means it also runs locally, without any
HEROS magic. Thus, the classes in this module do not inherit from LocalHERO. It is up to the user to make it a HERO or
to use BOSS as described in the following.

### Using as a HERO with BOSS
Using the [BOSS Object Starter Service (BOSS)](https://gitlab.com/atomiq-project/boss) it is easy to instantiate
objects of the classes provided in this repository and make them a [HERO](https://gitlab.com/atomiq-project/heros)
that is available through the network. To this end you can either install BOSS in your system and follow it's
instructions to create an object from the heros-devices module.

## Interfaces
To signal that a HERO provides a certain interface, herosdevices provides the submodule `interfaces`. Inheriting
from the classes therein enforces that particular methods and attributes are implemented by the HERO (otherwise it
errors upon initialization of the HERO) and signals it's compatibility through the hero metadata. This allows the
remote site to safely assume that a certain interface is present with the HERO. This allows to, for example, to
transparently use HEROs in an atomiq script as RFSource, VoltageSource, CurrentSource, DACChannel, Switch, etc. This is
explicitly possible without herosdevices depending on atomiq itself. The mechanism can easily be extended to have interface
classes for other systems as well.

.. note::
    The interfaces mechanism is completely optional. If a HERO does not inherit from an interface, nothing breaks but
    also none of the magic described above will happen on the remote side.