"""Задание 7: драйвер 10-битного АЦП MCP3021 на шине I2C."""

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

    def deinit(self):
        """Закрыть шину I2C."""
        self.bus.close()

    def get_number(self):
        """Прочитать два байта MCP3021 и вернуть код от 0 до 1023."""
        # Чтение в соответствии с шаблоном задания.
        # SMBus помещает первый принятый байт в младшие биты слова.
        data = self.bus.read_word_data(self.address, 0)
        lower_data_byte = (data >> 8) & 0xFF
        upper_data_byte = data & 0xFF

        # Первый байт: 0000 D9 D8 D7 D6.
        # Второй байт: D5 D4 D3 D2 D1 D0 X X.
        number = ((upper_data_byte & 0x0F) << 6) | (lower_data_byte >> 2)

        if self.verbose:
            print(
                f"Принятые данные: 0x{data:04X}; "
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
