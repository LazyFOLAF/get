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

    plt.title("Напряжение на входе АЦП последовательного счёта")
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


def plot_sampling_period_hist(time):
    """Построить гистограмму интервалов между соседними измерениями."""
    if len(time) < 2:
        print("Для гистограммы нужны хотя бы два момента измерений.")
        return

    sampling_periods = []
    for i in range(1, len(time)):
        sampling_periods.append(time[i] - time[i - 1])

    figure = plt.figure(figsize=(10, 6))
    plt.hist(sampling_periods)

    plt.title("Распределение периодов измерений АЦП последовательного счёта")
    plt.xlabel("Период измерений, с")
    plt.ylabel("Количество интервалов")
    plt.xlim(0, 0.06)

    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return figure
