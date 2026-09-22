import numpy as np
import time


def get_sin_wave_amplitude(freq, time):
    return (np.sin(2 * np.pi * freq * time) + 1) / 2


def get_triangle_wave_amplitude(freq, time):
    """
    Возвращает нормализованную амплитуду треугольного сигнала
    в диапазоне от 0 до 1 для заданной частоты и момента времени.
    """
    phase = (freq * time) % 1.0          # фаза в диапазоне [0, 1)
    if phase < 0.5:
        return phase * 2.0               # от 0 до 1
    else:
        return (1.0 - phase) * 2.0       # от 1 до 0


def wait_for_sampling_period(sampling_frequency):
    time.sleep(1.0 / sampling_frequency)