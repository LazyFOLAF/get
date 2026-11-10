"""Исследование RC-цепи, задание 1: график по реальным данным data.csv.

Поместите файл в get-rc рядом с data.csv и запустите:
    /usr/bin/python3 get-rc/rc_plot.py
Результат: get-rc/rc-plot.png, 300 dpi.

Можно указать другой CSV и выходной файл:
    python3 rc_plot.py /путь/data.csv --output /путь/rc-plot.png
"""

import argparse
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")  # Сохранение работает и без графического рабочего стола.
import matplotlib.pyplot as plt
import numpy as np


DEFAULT_CSV = Path(__file__).resolve().with_name("data.csv")


def load_measurements(path):
    """Прочитать время в секундах и напряжение в вольтах из CSV задания 2."""
    path = Path(path)
    with path.open(encoding="utf-8-sig") as source:
        header = source.readline().strip().lstrip("#").replace(" ", "")
    if header != "Время[с],Напряжение[В]":
        raise ValueError("первая строка CSV должна быть: Время[с],Напряжение[В]")

    data = np.loadtxt(path, delimiter=",", skiprows=1,
                      encoding="utf-8-sig", ndmin=2)
    if data.shape[0] < 2:
        raise ValueError("для графика нужны хотя бы две строки измерений")
    if data.shape[1] != 2:
        raise ValueError("в CSV должны быть ровно два столбца: время и напряжение")
    if not np.isfinite(data).all():
        raise ValueError("в CSV обнаружены NaN, бесконечность или пропуски")

    time_values = data[:, 0]
    voltage_values = data[:, 1]
    if np.any(np.diff(time_values) <= 0):
        raise ValueError("время в CSV должно строго возрастать; проверьте данные")
    return time_values, voltage_values


def make_figure(time_values, voltage_values):
    """Построить U(t) по всем исходным точкам с их фактическими временами."""
    figure, axes = plt.subplots(figsize=(10, 6))
    axes.plot(time_values, voltage_values, color="#225ea8", linewidth=1.3)
    axes.set_title("Напряжение на конденсаторе RC-цепи", fontsize=14, pad=14)
    axes.set_xlabel("Время, с", fontsize=12)
    axes.set_ylabel("Напряжение на конденсаторе, В", fontsize=12)

    axes.set_xlim(float(time_values[0]), float(time_values[-1]))
    lower = min(0.0, float(np.min(voltage_values)))
    upper = max(0.0, float(np.max(voltage_values)))
    padding = max((upper - lower) * 0.05, 0.02)
    axes.set_ylim(lower - padding if lower < 0 else 0, upper + padding)
    axes.minorticks_on()
    axes.grid(which="major", color="#b8c2cc", linewidth=0.7)
    axes.grid(which="minor", color="#dfe5eb", linewidth=0.4, linestyle=":")
    axes.set_axisbelow(True)
    figure.tight_layout()
    return figure


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="?", type=Path, default=DEFAULT_CSV,
                        help="CSV с измерениями; по умолчанию data.csv рядом со скриптом")
    parser.add_argument("--output", "-o", type=Path,
                        help="путь PNG; по умолчанию rc-plot.png рядом с CSV")
    args = parser.parse_args(argv)
    source = args.csv.expanduser().resolve()
    output = (args.output or source.with_name("rc-plot.png")).expanduser().resolve()

    if output == source:
        parser.error("выходной рисунок не должен заменять CSV с измерениями")
    if output.suffix.lower() != ".png":
        parser.error("для задания 1 укажите выходной файл с расширением .png")
    if not source.is_file():
        print(f"Не найден файл: {source}\n"
              "Сначала остановите запись RC-цепи через Ctrl+C: она сохранит data.csv.\n"
              "Поместите этот скрипт рядом с data.csv или укажите путь к CSV.",
              file=sys.stderr)
        return 1

    figure = None
    try:
        time_values, voltage_values = load_measurements(source)
        figure = make_figure(time_values, voltage_values)
        output.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(output, dpi=300, bbox_inches="tight")
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Не удалось построить график: {error}", file=sys.stderr)
        return 1
    finally:
        if figure is not None:
            plt.close(figure)

    print(f"Прочитано измерений: {len(time_values)}")
    print(f"График сохранён: {output} (300 dpi)")
    print("Вставьте PNG в отчёт, примените стили «Абзац рисунка» и «Рисунок»\n"
          "и добавьте подпись: «Зависимость напряжения на конденсаторе от времени».")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
