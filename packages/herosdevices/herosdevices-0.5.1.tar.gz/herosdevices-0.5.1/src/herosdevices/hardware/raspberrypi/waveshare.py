"""Driver for Waveshare SBC/microcontroller extension boards."""

from herosdevices.hardware.texas_instruments.ads1256 import ADS1256, ADS1256_CHANNEL, ADS1256_DRATE, ADS1256_GAIN
from herosdevices.interfaces import atomiq


class WaveshareADS1256(atomiq.ADCChannel):
    """This class represents one channel of the Waveshare ADS1256 ADC board.

    Multiple instances of this class can run in the same interpreter to access multiple channels.
    The configuration of the ADC will performed by the first instance. This means, gain data rate and reference
    voltage are only taken from the first instance.

    Args:
        posPin: Name of the pin receiving the positive voltage. I.e. AIN0 ... AIN7 or AINCOM
        negPin: Name of the pin receiving the negative voltage. I.e. AIN0 ... AIN7 or AINCOM. For non-differential
            measurements this is usually AINCOM.
        spi_bus: number of the SPI bus
        spi_device: number of the SPI device in bus.
        gain: gain to set in the PGIA
        drate: conversion rate of the ADS1256. See .ads1256.ADS1256_DRATE for valid values
        vref: Reference voltage given to the ADC. Usually 3.3V or 5V
        samples: number of samples to average when sending out measured values as heros datasource
    """

    def __init__(
        self,
        pos_pin: str = "AIN0",
        neg_pin: str = "AINCOM",
        spi_bus: int = 0,
        spi_device: int = 0,
        gain: int = 1,
        drate: str = "30000SPS",
        vref: float = 5.0,
        samples: int = 1,
    ) -> None:
        self.posPin = ADS1256_CHANNEL[pos_pin]
        self.negPin = ADS1256_CHANNEL[neg_pin]
        self.gain = ADS1256_GAIN[f"GAIN_{gain}"]
        self.drate = ADS1256_DRATE[f"DRATE_{drate}"]
        self.vref = vref
        self.samples = samples

        self._adc = ADS1256(spi_bus, spi_device, default_gain=self.gain, default_drate=self.drate)

    def _calculate_voltage(self, data: float) -> float:
        return self.vref * float(data) / (1 << 23) / int(self.gain.name.split("_")[-1])

    def measure(self, samples: int = 1, channel: str = "") -> float:  # noqa: ARG002
        """
        Measure the voltage by averaging multiple ADC samples.

        Args:
            samples (int): Number of samples to average.
            channel (str): Not used in this implementation.

        Returns:
            float: Measured voltage in volts.
        """
        v = 0
        for _ in range(samples):
            v += self._adc.get_channel_value(self.posPin, self.negPin)
        v /= samples

        return self._calculate_voltage(v)

    def _observable_data(self) -> tuple[float, str]:
        return self.measure(self.samples), "V"
