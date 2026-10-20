"""График напряжения и гистограмма периодов измерений АЦП."""

import matplotlib.pyplot as plt


def plot_voltage_vs_time(time, voltage, max_voltage):
    """Построить график U(t): время в секундах, напряжение в вольтах."""
    if len(time) != len(voltage):
        raise ValueError("Количество моментов времени и напряжений должно совпадать")
    if max_voltage <= 0:
        raise ValueError("Максимальное напряжение должно быть положительным")
    if len(time) == 0:
        print("Нет измерений для построения графика.")
        return

    figure = plt.figure(figsize=(10, 6))
    plt.plot(time, voltage, marker="o", markersize=3, linewidth=1)

    plt.title("Напряжение на входе АЦП")
    plt.xlabel("Время, с")
    plt.ylabel("Напряжение, В")

    # Используем фактические моменты измерений, включая последнюю точку.
    right_limit = max(time)
    plt.xlim(0, right_limit if right_limit > 0 else 1.0)
    plt.ylim(0, max_voltage)

    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return figure


def plot_sampling_period_hist(time, max_period=0.06):
    """Построить гистограмму интервалов между соседними измерениями."""
    if max_period is not None and max_period <= 0:
        raise ValueError("Верхняя граница периода должна быть положительной")
    if len(time) < 2:
        print("Для гистограммы нужны хотя бы два момента измерений.")
        return

    sampling_periods = []
    for i in range(1, len(time)):
        sampling_periods.append(time[i] - time[i - 1])

    figure = plt.figure(figsize=(10, 6))

    if max_period is None:
        # Для быстрого I2C-АЦП масштаб выбирается по фактическим периодам.
        largest_period = max(sampling_periods)
        right_limit = largest_period * 1.05 if largest_period > 0 else 1.0
        # Явный диапазон корректно отображает и одинаковые периоды.
        plt.hist(sampling_periods, bins=10, range=(0, right_limit))
    else:
        right_limit = max_period
        plt.hist(sampling_periods)

    plt.title("Распределение периодов измерений АЦП")
    plt.xlabel("Период измерений, с")
    plt.ylabel("Количество интервалов")
    plt.xlim(0, right_limit)

    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return figure
