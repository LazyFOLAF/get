"""Исследование RC-цепи, задание 2: получить реальные данные в data.csv.

Кнопка RC-платы не имеет отдельной линии GPIO: запуск определяется по
изменению напряжения SIG. Для сохранения опыта нажмите Ctrl+C.
"""

import argparse
from collections import deque
from datetime import datetime
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time

import numpy as np


HEADER = "Время[с],Напряжение[В]"
DEFAULT_OUTPUT = Path(__file__).resolve().with_name("data.csv")
BASELINE_SECONDS = 0.5


def collect_data(adc, samples, period=0.02, trigger_delta=0.05,
                 pretrigger=2.0, duration=None):
    """Добавлять пары (монотонное время, напряжение) в список samples.

    Исходный уровень фиксируется после устойчивого участка. Запуск — два
    последовательных отсчёта с отклонением не менее trigger_delta вольт.
    Сохраняются также точки из буфера до запуска. duration отсчитывается
    от обнаружения изменения; None означает запись до Ctrl+C.
    """
    history = deque()
    baseline_window = deque()
    baseline = None
    consecutive = 0
    trigger_time = None
    next_sample = time.perf_counter()
    next_status = next_sample

    print("Не нажимайте кнопку: определяю исходный уровень напряжения.")

    while True:
        read_start = time.perf_counter()
        voltage = float(adc.get_voltage())
        read_end = time.perf_counter()
        stamp = (read_start + read_end) / 2
        if not math.isfinite(voltage):
            raise ValueError("АЦП вернул некорректное напряжение")

        if trigger_time is None:
            history.append((stamp, voltage))
            # Оставляем одну точку на левой границе интервала.
            while len(history) > 1 and history[1][0] <= stamp - pretrigger:
                history.popleft()

            if baseline is None:
                baseline_window.append((stamp, voltage))
                while (len(baseline_window) > 1
                       and baseline_window[1][0] <= stamp - BASELINE_SECONDS):
                    baseline_window.popleft()
                values = [point[1] for point in baseline_window]
                enough_time = stamp - baseline_window[0][0] >= BASELINE_SECONDS
                if enough_time and max(values) - min(values) <= trigger_delta:
                    baseline = sum(values) / len(values)
                    print(f"Готово. Исходное напряжение: {baseline:.3f} В.")
                    print("Нажмите кнопку RC-платы. Затем можно отпускать и "
                          "снова нажимать её: все переходы попадут в запись.")
            else:
                if abs(voltage - baseline) >= trigger_delta:
                    consecutive += 1
                else:
                    consecutive = 0

                if consecutive >= 2:
                    trigger_time = stamp
                    samples.extend(history)
                    history.clear()
                    print("Изменение обнаружено. Запись началась.")
                    print("После окончания опыта нажмите Ctrl+C для сохранения.")
        else:
            # Одна пара добавляется целиком, в том числе перед Ctrl+C.
            samples.append((stamp, voltage))

        if stamp >= next_status:
            if trigger_time is None:
                state = "ожидание кнопки" if baseline is not None else "подготовка"
                print(f"U = {voltage:.3f} В; {state}")
            else:
                print(f"Запись: {stamp - trigger_time:.1f} с; "
                      f"U = {voltage:.3f} В; точек: {len(samples)}")
            next_status = stamp + 1.0

        if (trigger_time is not None and duration is not None
                and stamp - trigger_time >= duration):
            return

        # Реальное время каждого измерения сохраняется отдельно. Пропущенные
        # из-за задержек ОС такты не подменяются искусственными точками.
        next_sample += period
        now = time.perf_counter()
        if next_sample > now:
            time.sleep(next_sample - now)
        else:
            next_sample = now


def save_data(samples, output):
    """Сохранить CSV по инструкции курса; вернуть путь резервной копии."""
    if not samples:
        raise ValueError("Нет измерений для сохранения")

    origin = samples[0][0]
    time_values = [stamp - origin for stamp, voltage in samples]
    voltage_values = [voltage for stamp, voltage in samples]
    data = np.column_stack((time_values, voltage_values))
    if not np.isfinite(data).all() or np.any(np.diff(data[:, 0]) <= 0):
        raise ValueError("В данных есть некорректные значения времени или напряжения")

    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".rc_", suffix=".tmp", dir=output.parent)
    os.close(fd)
    temporary = Path(name)
    backup = None
    try:
        # Те же заголовок, разделитель, кодировка и формат, что в задании.
        np.savetxt(temporary, data, delimiter=",", fmt="%.4f",
                   header=HEADER, comments="", encoding="utf-8")
        if output.exists():
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            backup = output.with_name(f"{output.stem}_{stamp}{output.suffix}")
            shutil.copy2(output, backup)
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return backup


def positive_number(text):
    value = float(text)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("требуется положительное конечное число")
    return value


def nonnegative_number(text):
    value = float(text)
    if not math.isfinite(value) or value < 0:
        raise argparse.ArgumentTypeError("требуется неотрицательное конечное число")
    return value


def check_input(adc, vref):
    """Показать сырые байты, код АЦП и напряжение без запуска опыта."""
    print("Прямое чтение MCP3021. Нажимайте и отпускайте кнопку RC-платы.")
    print("Для выхода нажмите Ctrl+C. CSV в этом режиме не создаётся.")
    while True:
        number = adc.get_number()
        first, second = adc.last_bytes
        voltage = number / 1024 * vref
        print(f"RAW: 0x{first:02X} 0x{second:02X}; "
              f"код: {number:4d}; U: {voltage:.4f} В", flush=True)
        time.sleep(0.2)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vref", type=positive_number, default=5.0,
                        help="измеренное питание АЦП, В; пример по умолчанию: 5.0")
    parser.add_argument("--period", type=positive_number, default=0.02,
                        help="желаемый период измерений, с; по умолчанию: 0.02")
    parser.add_argument("--trigger", type=positive_number, default=0.05,
                        help="отклонение от исходного уровня для запуска, В; 0.05")
    parser.add_argument("--pretrigger", type=nonnegative_number, default=2.0,
                        help="буфер перед обнаружением изменения, с; 2.0")
    parser.add_argument("--duration", type=positive_number, default=None,
                        help="секунды записи после запуска; без параметра — до Ctrl+C")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="выходной CSV; по умолчанию data.csv рядом со скриптом")
    parser.add_argument("--check", action="store_true",
                        help="показать сырые байты, код и напряжение без записи CSV")
    args = parser.parse_args(argv)
    if args.period < 0.001:
        parser.error("--period должен быть не менее 0.001 с")

    # Импорт здесь позволяет прочитать --help без открытия I2C.
    from mcp3021_driver import MCP3021

    adc = None
    samples = []
    exit_code = 0
    try:
        adc = MCP3021(args.vref)
        if args.check:
            check_input(adc, args.vref)
        else:
            # Первое прямое чтение выполняется до ожидания нажатия.
            adc.get_voltage()
            collect_data(adc, samples, period=args.period,
                         trigger_delta=args.trigger, pretrigger=args.pretrigger,
                         duration=args.duration)
    except KeyboardInterrupt:
        print("\nИзмерения остановлены.")
    except (OSError, ValueError) as error:
        print(f"Ошибка измерения: {error}", file=sys.stderr)
        exit_code = 1
    finally:
        try:
            if adc is not None:
                adc.deinit()
        except OSError as error:
            print(f"Ошибка закрытия I2C: {error}", file=sys.stderr)
            exit_code = 1

        if samples:
            try:
                backup = save_data(samples, args.output)
                elapsed = samples[-1][0] - samples[0][0]
                print(f"Сохранено {len(samples)} точек за {elapsed:.3f} с.")
                print(f"Файл: {args.output.resolve()}")
                if backup is not None:
                    print(f"Предыдущий опыт сохранён: {backup.name}")
            except (OSError, ValueError) as error:
                print(f"Не удалось сохранить данные: {error}", file=sys.stderr)
                exit_code = 1
        elif not args.check:
            print("Изменение напряжения не обнаружено; новый CSV не создан.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
