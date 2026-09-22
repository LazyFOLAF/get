import RPi.GPIO as GPIO


class PWM_DAC:
    def __init__(self, gpio_pin, pwm_frequency, dynamic_range, verbose=False):
        self.gpio_pin = gpio_pin
        self.pwm_frequency = pwm_frequency
        self.dynamic_range = dynamic_range
        self.verbose = verbose

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT, initial=0)

        # Создаём объект ШИМ с заданной частотой
        self.pwm = GPIO.PWM(self.gpio_pin, self.pwm_frequency)
        # Запускаем ШИМ с нулевой скважностью
        self.pwm.start(0)

    def deinit(self):
        # Останавливаем генерацию ШИМ
        self.pwm.stop()
        # Сбрасываем настройки GPIO
        GPIO.output(self.gpio_pin, 0)
        GPIO.cleanup()

    def set_voltage(self, voltage):
        """
        Принимает вещественное напряжение и выставляет его на выходе ЦАП,
        изменяя коэффициент заполнения ШИМ.
        """
        if not (0.0 <= voltage <= self.dynamic_range):
            print(f"Напряжение выходит за динамический диапазон ЦАП "
                  f"(0.00 - {self.dynamic_range:.2f} В)")
            print("Устанавливаем 0.0 В")
            duty_cycle = 0.0
        else:
            duty_cycle = voltage / self.dynamic_range * 100.0

        self.pwm.ChangeDutyCycle(duty_cycle)

        if self.verbose:
            print(f"Напряжение: {voltage:.3f} В, "
                  f"коэффициент заполнения: {duty_cycle:.2f}%")


if __name__ == "__main__":
    try:
        dac = PWM_DAC(12, 500, 3.290, True)

        while True:
            try:
                voltage = float(input("Введите напряжение в Вольтах: "))
                dac.set_voltage(voltage)

            except ValueError:
                print("Вы ввели не число. Попробуйте ещё раз\n")

    finally:
        dac.deinit()