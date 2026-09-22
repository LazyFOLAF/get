import r2r_dac as r2r
import signal_generator as sg
import time

# Параметры генерируемого сигнала
amplitude = 3.0             # В
signal_frequency = 10       # Гц
sampling_frequency = 1000   # Гц

try:
    # Создаём объект класса для управления R2R-ЦАП
    dac = r2r.R2R_DAC([16, 20, 21, 25, 26, 17, 27, 22], 3.183, False)

    t = 0.0
    dt = 2.0 / sampling_frequency

    while True:
        # Получаем нормализованную амплитуду (0..1) в момент времени t
        normalized = sg.get_triangle_wave_amplitude(signal_frequency, t)
        # Масштабируем на заданную амплитуду и выставляем на ЦАП
        dac.set_voltage(normalized * amplitude)

        # Ждём один период дискретизации
        sg.wait_for_sampling_period(sampling_frequency)

        # Переходим к следующему моменту времени
        t += dt

finally:
    # Сбрасываем настройки GPIO
    dac.deinit()