import RPi.GPIO as GPIO


class R2R_DAC:
    def __init__(self, gpio_bits, dynamic_range, verbose=False):
        self.gpio_bits = gpio_bits
        self.dynamic_range = dynamic_range
        self.verbose = verbose

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_bits, GPIO.OUT, initial=0)

    def deinit(self):
        GPIO.output(self.gpio_bits, 0)
        GPIO.cleanup()

    def set_number(self, number):
        """
        Принимает целое число 0..255 и подаёт его двоичное представление
        на вход R2R-ЦАП.
        """
        # Ограничиваем число диапазоном 8 бит
        if number < 0:
            number = 0
        elif number > 255:
            number = 255

        # Двоичное представление: строка из 8 бит от старшего к младшему
        binary_string = f"{number:08b}"

        # Подаём биты на соответствующие GPIO-пины
        for bit, pin in zip(binary_string, self.gpio_bits):
            GPIO.output(pin, int(bit))

        if self.verbose:
            print(f"Число: {number}, биты: {binary_string}")

    def set_voltage(self, voltage):
        """
        Принимает вещественное напряжение и выставляет его на выходе ЦАП,
        преобразуя в число и вызывая set_number.
        """
        if not (0.0 <= voltage <= self.dynamic_range):
            print(f"Напряжение выходит за динамический диапазон ЦАП "
                  f"(0.00 - {self.dynamic_range:.2f} В)")
            print("Устанавливаем 0.0 В")
            number = 0
        else:
            number = int(voltage / self.dynamic_range * 255)

        self.set_number(number)


if __name__ == "__main__":
    try:
        dac = R2R_DAC([16, 20, 21, 25, 26, 17, 27, 22], 3.183, True)

        while True:
            try:
                voltage = float(input("Введите напряжение в Вольтах: "))
                dac.set_voltage(voltage)

            except ValueError:
                print("Вы ввели не число. Попробуйте ещё раз\n")

    finally:
        dac.deinit()