"""8-битный АЦП последовательного счёта и приближения на плате get-adc."""

import time

import RPi.GPIO as GPIO


class R2R_ADC:
    """dynamic_range — измеренное напряжение ЦАП при коде 255, в вольтах."""

    def __init__(self, dynamic_range, compare_time=0.01, verbose=False):
        if dynamic_range <= 0:
            raise ValueError("Динамический диапазон должен быть положительным")
        if compare_time < 0:
            raise ValueError("Время сравнения не может быть отрицательным")

        self.dynamic_range = dynamic_range
        self.compare_time = compare_time
        self.verbose = verbose

        # Пины перечислены от старшего бита (bit7) к младшему (bit0).
        self.bits_gpio = [26, 20, 19, 16, 13, 12, 25, 11]
        self.comp_gpio = 21
        self.max_number = 2 ** len(self.bits_gpio) - 1  # 255

        GPIO.setmode(GPIO.BCM)
        try:
            GPIO.setup(self.bits_gpio, GPIO.OUT, initial=0)
            GPIO.setup(self.comp_gpio, GPIO.IN)
        except BaseException:
            GPIO.cleanup(self.bits_gpio + [self.comp_gpio])
            raise

    def deinit(self):
        """Обнулить ЦАП и освободить GPIO, используемые этим объектом."""
        try:
            GPIO.output(self.bits_gpio, 0)
        finally:
            GPIO.cleanup(self.bits_gpio + [self.comp_gpio])

    def number_to_dac(self, number):
        """Подать целое число от 0 до 255 на параллельный вход ЦАП."""
        if not isinstance(number, int):
            raise TypeError("Код ЦАП должен быть целым числом")
        if not 0 <= number <= self.max_number:
            raise ValueError("Код ЦАП должен находиться в диапазоне 0–255")

        bits = [int(bit) for bit in f"{number:08b}"]
        GPIO.output(self.bits_gpio, bits)

        if self.verbose:
            print(f"Код ЦАП: {number:3d}; биты: {bits}")

    def sequential_counting_adc(self):
        """Вернуть первый код, при котором U_ЦАП > U_вход, или 255."""
        for number in range(self.max_number + 1):
            self.number_to_dac(number)
            time.sleep(self.compare_time)

            # На плате get-adc HIGH означает U_ЦАП > U_вход.
            if GPIO.input(self.comp_gpio) == GPIO.HIGH:
                return number

        # Входное напряжение не оказалось ниже напряжения ЦАП при коде 255.
        return self.max_number

    def get_sc_voltage(self):
        """Измерить входное напряжение методом последовательного счёта."""
        number = self.sequential_counting_adc()
        return number / self.max_number * self.dynamic_range

    def successive_approximation_adc(self):
        """Определить код за 8 сравнений, начиная со старшего бита."""
        number = 0

        for bit in range(len(self.bits_gpio) - 1, -1, -1):
            # Пробуем установить очередной бит, сохраняя уже найденные.
            trial_number = number | (1 << bit)
            self.number_to_dac(trial_number)
            time.sleep(self.compare_time)

            # HIGH означает U_ЦАП > U_вход: пробный бит оставляем нулём.
            # При LOW пробный код не превышает вход, поэтому сохраняем бит.
            if GPIO.input(self.comp_gpio) == GPIO.LOW:
                number = trial_number

        # После отклонения последнего пробного бита на ЦАП мог остаться
        # пробный код. Выводим именно итоговый результат преобразования.
        self.number_to_dac(number)
        return number

    def get_sar_voltage(self):
        """Измерить напряжение методом последовательного приближения."""
        number = self.successive_approximation_adc()
        return number / self.max_number * self.dynamic_range


if __name__ == "__main__":
    # 3.3 В — пример. Замените на измеренное мультиметром U_ЦАП(255).
    DYNAMIC_RANGE = 3.3

    adc = None
    try:
        adc = R2R_ADC(DYNAMIC_RANGE)
        print("АЦП последовательного приближения. Для остановки нажмите Ctrl+C.")

        while True:
            voltage = adc.get_sar_voltage()
            print(f"Напряжение: {voltage:.3f} В", flush=True)

    except KeyboardInterrupt:
        print("\nИзмерения остановлены.")

    finally:
        if adc is not None:
            adc.deinit()
