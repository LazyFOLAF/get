"""Задание 5: график напряжения АЦП последовательного приближения."""

import time

from adc_plot import plot_voltage_vs_time
from r2r_adc import R2R_ADC


# Замените пример на измеренное мультиметром напряжение ЦАП при коде 255.
DYNAMIC_RANGE = 3.3
DURATION = 3.0          # Продолжительность сбора данных, с.
COMPARE_TIME = 0.0001   # Пауза для компаратора после каждого кода ЦАП, с.


def main():
    if DURATION <= 0:
        raise ValueError("Продолжительность измерений должна быть положительной")

    voltage_values = []
    time_values = []
    adc = None

    try:
        adc = R2R_ADC(DYNAMIC_RANGE, compare_time=COMPARE_TIME)
        print(f"Измерение методом последовательного приближения: {DURATION:.2f} с...")
        start_time = time.perf_counter()

        while time.perf_counter() - start_time < DURATION:
            voltage = adc.get_sar_voltage()
            elapsed_time = time.perf_counter() - start_time

            voltage_values.append(voltage)
            time_values.append(elapsed_time)

        print(f"Получено измерений: {len(voltage_values)}")
        plot_voltage_vs_time(time_values, voltage_values, DYNAMIC_RANGE)

    except KeyboardInterrupt:
        print("\nИзмерения остановлены.")

    finally:
        if adc is not None:
            adc.deinit()


if __name__ == "__main__":
    main()
