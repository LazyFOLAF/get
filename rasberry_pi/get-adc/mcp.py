"""Задания 8 и 9: график напряжения MCP3021 и гистограмма периодов."""

import time

from adc_plot import plot_sampling_period_hist, plot_voltage_vs_time
from mcp3021_driver import MCP3021


# Замените пример на измеренное напряжение PWR блока AUX относительно GND.
DYNAMIC_RANGE = 5.0
DURATION = 3.0         # Продолжительность сбора данных, с.
SHOW_HISTOGRAM = True  # Задание 8: False. Задания 8 и 9 вместе: True.


def main():
    if DURATION <= 0:
        raise ValueError("Продолжительность измерений должна быть положительной")

    voltage_values = []
    time_values = []
    adc = None

    try:
        adc = MCP3021(DYNAMIC_RANGE)
        print(f"Измерение напряжения MCP3021 в течение {DURATION:.2f} с...")
        start_time = time.perf_counter()

        while time.perf_counter() - start_time < DURATION:
            voltage = adc.get_voltage()
            elapsed_time = time.perf_counter() - start_time

            voltage_values.append(voltage)
            time_values.append(elapsed_time)

        print(f"Получено измерений: {len(voltage_values)}")
        plot_voltage_vs_time(time_values, voltage_values, DYNAMIC_RANGE)

        if SHOW_HISTOGRAM:
            plot_sampling_period_hist(time_values, max_period=None)

    except KeyboardInterrupt:
        print("\nИзмерения остановлены.")

    finally:
        if adc is not None:
            adc.deinit()


if __name__ == "__main__":
    main()
