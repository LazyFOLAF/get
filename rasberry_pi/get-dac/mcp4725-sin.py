import mcp4725_driver as mcp
import signal_generator as sg
import time

# Параметры генерируемого сигнала
amplitude = 4.5             # В
signal_frequency = 50       # Гц
sampling_frequency = 500   # Гц

try:
    # Создаём объект класса для управления микросхемой MCP4725 по I2C
    dac = mcp.MCP4725(5.0, 0x61, False)

    t = 0.0
    dt = 1.0 / sampling_frequency

    while True:
        # Получаем нормализованную амплитуду (0..1) в момент времени t
        normalized = sg.get_sin_wave_amplitude(signal_frequency, t)
        # Масштабируем на заданную амплитуду и выставляем на ЦАП
        dac.set_voltage(normalized * amplitude)

        # Ждём один период дискретизации
        sg.wait_for_sampling_period(sampling_frequency)

        # Переходим к следующему моменту времени
        t += dt

finally:
    # Закрываем шину I2C
    dac.deinit()