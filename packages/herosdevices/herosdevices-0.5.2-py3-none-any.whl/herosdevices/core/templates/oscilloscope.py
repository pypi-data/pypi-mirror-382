"""Templates for creating oscilloscope representations."""

from herosdevices.core.templates.acq_device import AcquisitionDeviceTemplate


class OscilloscopeTemplate(AcquisitionDeviceTemplate):
    """
    Template (base class) for oscilloscope.

    To make a functional oscilloscope, the user needs to implement all abstract methods.
    In addition, this call does not cover the mechanism the actually retrieve the image buffers
    from the device since it is typically special to each oscilloscope vendor/API. A general guideline
    should be to start a separate thread for the acquisition which uses the _acquisition_lock
    to prohibit concurrent exposures. For each received image, the event :meth:`acquisition_data`
    should be called. In addition, :meth:`acquisition_stopped` should be emitted
    after the acquisition.
    """

    get_scope = AcquisitionDeviceTemplate.get_device
