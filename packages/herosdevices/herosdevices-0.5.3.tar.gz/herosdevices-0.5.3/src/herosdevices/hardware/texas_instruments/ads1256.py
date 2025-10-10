"""Drivers for the ADS1256 24-Bit, 30kSPS, 8-Channel ADC."""

# TODO: make gpiod and spidev optional dependencies
import time
from enum import Enum

import gpiod
import spidev  # type: ignore

from herosdevices.helper import log


class ADS1256_CHANNEL(Enum):
    """Multiplexer channel."""

    AIN0 = 0
    AIN1 = 1
    AIN2 = 2
    AIN3 = 3
    AIN4 = 4
    AIN5 = 5
    AIN6 = 6
    AIN7 = 7
    AINCOM = 8


class ADS1256_GAIN(Enum):
    """Gain of the programmable gain amplifier.

    For voltage ranges for each gain settings refer to ADS1256 datasheet Table 8.
    """

    GAIN_1 = 0  # GAIN   1
    GAIN_2 = 1  # GAIN   2
    GAIN_4 = 2  # GAIN   4
    GAIN_8 = 3  # GAIN   8
    GAIN_16 = 4  # GAIN  16
    GAIN_32 = 5  # GAIN  32
    GAIN_64 = 6  # GAIN  64


class ADS1256_DRATE(Enum):
    """Possible A/D Datarates.

    Refer to table: DRATE: A/D Data Rate (Address 03h) in the datasheet for more information.
    """

    DRATE_30000SPS = 0xF0  # reset the default values
    DRATE_15000SPS = 0xE0
    DRATE_7500SPS = 0xD0
    DRATE_3750SPS = 0xC0
    DRATE_2000SPS = 0xB0
    DRATE_1000SPS = 0xA1
    DRATE_500SPS = 0x92
    DRATE_100SPS = 0x82
    DRATE_60SPS = 0x72
    DRATE_50SPS = 0x63
    DRATE_30SPS = 0x53
    DRATE_25SPS = 0x43
    DRATE_15SPS = 0x33
    DRATE_10SPS = 0x20
    DRATE_5SPS = 0x13
    DRATE_2d5SPS = 0x03


class ADS1256_REG(Enum):
    """Registers of the ADS1256."""

    STATUS = 0  # x1H
    MUX = 1  # 01H
    ADCON = 2  # 20H
    DRATE = 3  # F0H
    IO = 4  # E0H
    OFC0 = 5  # xxH
    OFC1 = 6  # xxH
    OFC2 = 7  # xxH
    FSC0 = 8  # xxH
    FSC1 = 9  # xxH
    FSC2 = 10  # xxH


# command definition
class ADS1256_CMD(Enum):
    """Command definitions.

    Refer to table 24 in the datasheet for details.
    """

    WAKEUP = 0x00  # Completes SYNC and Exits Standby Mode 0000  0000 (00h)
    RDATA = 0x01  # Read Data 0000  0001 (01h)
    RDATAC = 0x03  # Read Data Continuously 0000   0011 (03h)
    SDATAC = 0x0F  # Stop Read Data Continuously 0000   1111 (0Fh)
    RREG = 0x10  # Read from REG rrr 0001 rrrr (1xh)
    WREG = 0x50  # Write to REG rrr 0101 rrrr (5xh)
    # Offset and Gain Self-Calibration 1111    0000 (F0h)
    SELFCAL = 0xF0
    SELFOCAL = 0xF1  # Offset Self-Calibration 1111    0001 (F1h)
    SELFGCAL = 0xF2  # Gain Self-Calibration 1111    0010 (F2h)
    SYSOCAL = 0xF3  # System Offset Calibration 1111   0011 (F3h)
    SYSGCAL = 0xF4  # System Gain Calibration 1111    0100 (F4h)
    # Synchronize the A/D Conversion 1111   1100 (FCh)
    SYNC = 0xFC
    STANDBY = 0xFD  # Begin Standby Mode 1111   1101 (FDh)
    RESET = 0xFE  # Reset to Power-Up Values 1111   1110 (FEh)


def delay_us(delay: int) -> None:
    """Delay execution by `delay` microseconds (Uses sleep function).

    Args:
        delay: delay in microseconds.
    """
    time.sleep(delay / 1e6)


class ADS1256:
    """Interfacing the ADS1256 SPI ADC (as e.g. used on the Waveshare high-precision AD-DA board)."""

    _instances = []
    _init_done = False

    def __new__(cls, *args, **_kwargs) -> "ADS1256":
        """Avoid SPI conflict when multiple instances of same bus are requested.

        Two instances working concurrently on the same bus might mess things up. We thus return the running instance
        if a second instance with the same SPI parameters is requested
        """
        running_inst = [
            inst["object"] for inst in cls._instances if inst["bus"] == args[0] and inst["device"] == args[1]
        ]
        if len(running_inst) == 0:
            instance = object.__new__(cls)
            cls._instances.append({"bus": args[0], "device": args[1], "object": instance})
        else:
            instance = running_inst[0]
            log.warning(
                "A second instance of ADS1256 on the same SPI bus was requested. Returned the existing instance"
            )
        return instance

    def __init__(
        self,
        spi_bus: int = 0,
        spi_device: int = 0,
        cs_pin: int = 22,
        rst_pin: int = 18,
        drdy_pin: int = 17,
        spi=None,  # noqa: ANN001 TODO: no idea what the type is here, needs to be checked
        gpio_device: str = "/dev/gpiochip0",
        default_gain: ADS1256_GAIN = ADS1256_GAIN.GAIN_1,
        default_drate: ADS1256_DRATE = ADS1256_DRATE.DRATE_30000SPS,
    ) -> None:
        """
        Interfacing the ADS1256 SPI ADC (as e.g. used on the Waveshare high-precision AD-DA board).

        Args:
            spi_bus: Number of the SPI bus the ADS1256 is attached to
            spi_device: Device number at the SPI bus the ADS1256 is attached to
            cs_pin: Pin number of the chip select pin
            rst_pin: pin number of the reset pin
            drdy_pin: pin number of the data ready pin
            spi: optional spidev device. If this is given, spi_bus and spi_device are ignored.
            gpio_device: full path to kernel character device that holds the needed gpios. Typically "/dev/gpiochip0"
            default_gain: default gain to set when initializing the device
            default_drate: default data rate to set when initializing the device
        """
        if not self._init_done:
            # init SPI bus
            self._spi = spi if spi is not None else spidev.SpiDev(spi_bus, spi_device)
            self.scan_mode = 0

            self._spi.max_speed_hz = 20000
            self._spi.mode = 0b01

            # init GPIOs
            self.gpio_chip = gpiod.Chip(gpio_device)
            self.gpios = self.gpio_chip.request_lines(
                consumer="ADS1256",
                config={
                    cs_pin: gpiod.LineSettings(direction=gpiod.line.Direction.OUTPUT),
                    rst_pin: gpiod.LineSettings(direction=gpiod.line.Direction.OUTPUT),
                    drdy_pin: gpiod.LineSettings(direction=gpiod.line.Direction.INPUT, bias=gpiod.line.Bias.PULL_UP),
                },
            )
            self.cs_pin = cs_pin
            self.rst_pin = rst_pin
            self.drdy_pin = drdy_pin

            self.reset()

            if self._read_chip_id() == 3:  # noqa: PLR2004 TODO: this seems specific. Isn't this different for each chip?
                log.info("ID Read successful")
            else:
                log.warning("ID Read failed")

            self.config_adc(default_gain, default_drate)

            self._init_done = True

    # Hardware reset
    def reset(self) -> None:
        """Reset the chip by pulsing the reset pin."""
        self.gpios.set_value(self.rst_pin, gpiod.line.Value.ACTIVE)
        time.sleep(200 / 1000)
        self.gpios.set_value(self.rst_pin, gpiod.line.Value.INACTIVE)
        time.sleep(200 / 1000)
        self.gpios.set_value(self.rst_pin, gpiod.line.Value.ACTIVE)

    def _write_cmd(self, cmd: ADS1256_CMD) -> None:
        """Run a command on the chip."""
        self.gpios.set_value(self.cs_pin, gpiod.line.Value.INACTIVE)  # cs  0
        self._spi.writebytes([cmd.value])
        self.gpios.set_value(self.cs_pin, gpiod.line.Value.ACTIVE)  # cs 1

    def _write_reg(self, reg: ADS1256_REG, data: int) -> None:
        """Write data to a register."""
        self.gpios.set_value(self.cs_pin, gpiod.line.Value.INACTIVE)  # cs  0
        self._spi.writebytes([ADS1256_CMD.WREG.value | reg.value, 0x00, data])
        self.gpios.set_value(self.cs_pin, gpiod.line.Value.ACTIVE)  # cs 1

    def _read_data(self, reg: ADS1256_REG) -> list:
        """Read data from a register."""
        self.gpios.set_value(self.cs_pin, gpiod.line.Value.INACTIVE)  # cs  0
        self._spi.writebytes([ADS1256_CMD.RREG.value | reg.value, 0x00])
        data = self._spi.readbytes(1)
        self.gpios.set_value(self.cs_pin, gpiod.line.Value.ACTIVE)  # cs 1

        return data

    def _wait_drdy(self) -> None:
        """Wait for the DRDY (Data Ready) pin to be low."""
        for _ in range(0, 400000, 1):  # TODO: With this, the timeout is execution speed dependent, needs fixing!
            if self.gpios.get_value(self.drdy_pin) == gpiod.line.Value.INACTIVE:
                break
        else:
            log.warning("Time out when waiting for data ready...")
            # TODO: maybe include a return value. Calling functions can not know if data is ready or not.

    def _read_chip_id(self) -> int:
        self._wait_drdy()
        status = self._read_data(ADS1256_REG.STATUS)
        return status[0] >> 4

    # The configuration parameters of ADC, gain and data rate
    def config_adc(self, gain: ADS1256_GAIN, drate: ADS1256_DRATE) -> None:
        """Configure the gain and datarate of the ADC."""
        self._wait_drdy()
        buf = [0, 0, 0, 0, 0, 0, 0, 0]
        buf[0] = (0 << 3) | (1 << 2) | (0 << 1)
        buf[1] = 0x08
        buf[2] = (0 << 5) | (0 << 3) | (gain.value << 0)
        buf[3] = drate.value

        self.gpios.set_value(self.cs_pin, gpiod.line.Value.INACTIVE)  # cs  0
        self._spi.writebytes([ADS1256_CMD.WREG.value | 0, 0x03])
        self._spi.writebytes(buf)

        self.gpios.set_value(self.cs_pin, gpiod.line.Value.ACTIVE)  # cs 1
        time.sleep(1 / 1000)

    def self_calibration(self) -> None:
        """Run offset and gain self calibration."""
        self._write_cmd(ADS1256_CMD.SELFCAL)
        self._wait_drdy()

    def set_channel(self, pos_channel: ADS1256_CHANNEL, neg_channel: ADS1256_CHANNEL = ADS1256_CHANNEL.AINCOM) -> None:
        """Set channel of the input multiplexer.

        The multiplexer performs a differential measurement between `pos_channel` and `neg_channel`. Details can be
        found in the datasheet under "Input Multiplexer".

        Args:
            pos_channel: Positive channel.
            neg_channel: Negative channel. Defaults to AINCOM (non-differential measurement).
        """
        self._write_reg(ADS1256_REG.MUX, (pos_channel.value << 4) | neg_channel.value)

    def set_scan_mode(self, mode):  # noqa: ANN201 ANN001 D102
        # TODO: seems to do nothing...
        self.scan_mode = mode

    def read_adc_data(self) -> int:
        """Read ADC value from the currently active channel in bits."""
        self._wait_drdy()
        self.gpios.set_value(self.cs_pin, gpiod.line.Value.INACTIVE)  # cs  0
        self._spi.writebytes([ADS1256_CMD.RDATA.value])
        delay_us(10)

        buf = self._spi.readbytes(3)
        self.gpios.set_value(self.cs_pin, gpiod.line.Value.ACTIVE)  # cs 1

        return int.from_bytes(buf, "big", signed=True)

    def get_channel_value(
        self, pos_channel: ADS1256_CHANNEL, neg_channel: ADS1256_CHANNEL = ADS1256_CHANNEL.AINCOM
    ) -> int:
        """Read ADC value from the given channel in bits either single-ended or differential."""
        self.set_channel(pos_channel, neg_channel)
        self._write_cmd(ADS1256_CMD.SYNC)
        delay_us(10)
        self._write_cmd(ADS1256_CMD.WAKEUP)
        delay_us(10)
        return self.read_adc_data()

    def get_all(self) -> list[int]:
        """Read ADC for all channels subsequently."""
        return [self.get_channel_value(channel) for channel in ADS1256_CHANNEL]
