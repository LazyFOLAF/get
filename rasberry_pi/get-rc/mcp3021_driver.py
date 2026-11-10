"""Задание 7: драйвер 10-битного АЦП MCP3021 на шине I2C."""

import errno
import fcntl
import os
import time

import smbus


class MCP3021:
    """dynamic_range — измеренное напряжение питания АЦП, в вольтах."""

    def __init__(self, dynamic_range, verbose=False):
        if dynamic_range <= 0:
            raise ValueError("Динамический диапазон должен быть положительным")

        self.dynamic_range = dynamic_range
        self.address = 0x4D
        self.verbose = verbose
        self.resolution = 10
        self.bus = smbus.SMBus(1)
        self._raw_fd = None
        self._closed = False

    def deinit(self):
        """Закрыть все открытые дескрипторы I2C."""
        if self._closed:
            return
        self._closed = True
        try:
            if self._raw_fd is not None:
                os.close(self._raw_fd)
                self._raw_fd = None
        finally:
            self.bus.close()

    def _read_bytes(self):
        """Чтение по шаблону, при отказе — прямое чтение I2C в Linux."""
        if self._closed:
            raise ValueError("Шина I2C уже закрыта")

        if self._raw_fd is None:
            try:
                word = self.bus.read_word_data(self.address, 0)
            except OSError as error:
                if error.errno not in (errno.EIO, errno.EREMOTEIO, errno.ETIMEDOUT):
                    raise
                # MCP3021 не имеет регистра 0. read_word_data() посылает
                # командный байт, который АЦП может не подтвердить.
                # Обычный smbus не предоставляет прямого чтения двух байтов.
                # Для этого используем стандартный интерфейс i2c-dev Linux.
                fd = os.open("/dev/i2c-1", os.O_RDWR)
                try:
                    fcntl.ioctl(fd, 0x0703, self.address)  # I2C_SLAVE
                except BaseException:
                    os.close(fd)
                    raise
                self._raw_fd = fd
                if self.verbose:
                    print("Переключение на прямое чтение двух байтов I2C.")
            else:
                # SMBus помещает первый принятый байт в младшие биты слова.
                return word & 0xFF, (word >> 8) & 0xFF

        # Оба байта одной выборки читаются ОДНИМ запросом без байта команды.
        data = os.read(self._raw_fd, 2)
        if len(data) != 2:
            raise OSError(errno.EIO, "MCP3021 вернул менее двух байтов")
        return data[0], data[1]

    def get_number(self):
        """Прочитать два байта MCP3021 и вернуть код от 0 до 1023."""
        upper_data_byte, lower_data_byte = self._read_bytes()

        # Первый байт: 0000 D9 D8 D7 D6.
        # Второй байт: D5 D4 D3 D2 D1 D0 X X.
        number = ((upper_data_byte & 0x0F) << 6) | (lower_data_byte >> 2)

        if self.verbose:
            print(
                f"первый байт: 0x{upper_data_byte:02X}; "
                f"второй байт: 0x{lower_data_byte:02X}; "
                f"число: {number}"
            )

        return number

    def get_voltage(self):
        """Прочитать напряжение: U = код * U_питания / 1024."""
        number = self.get_number()
        return number / (1 << self.resolution) * self.dynamic_range


if __name__ == "__main__":
    # 5.0 В — пример. Подставьте измеренное напряжение PWR блока AUX
    # относительно GND при установленной перемычке питания на 5V.
    DYNAMIC_RANGE = 5.0

    adc = None
    try:
        adc = MCP3021(DYNAMIC_RANGE)
        print(f"Запущен файл: {__file__}", flush=True)
        print("10-битный АЦП MCP3021. Для остановки нажмите Ctrl+C.")

        while True:
            voltage = adc.get_voltage()
            print(f"Напряжение: {voltage:.3f} В", flush=True)
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nИзмерения остановлены.")

    finally:
        if adc is not None:
            adc.deinit()
