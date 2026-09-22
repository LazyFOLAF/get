import RPi.GPIO as GPIO
dac_bits=[16, 20, 21, 25, 26, 17, 27, 22]

GPIO.setmode(GPIO.BCM)
GPIO.setup(dac_bits, GPIO.OUT)
dinamic_range = 3.3

def voltage_to_number(voltage):
    if not (0.0 <= voltage <= dinamic_range):
        print("Напряжение выходит за динамический диапазон ЦАП (0.00 - {dynamic_range:.2f} B)")
        print("Устанавливаем 0.0 В")
        return 0
    return int(voltage / dinamic_range * 255)

def number_to_dac(number):
    if number < 0:
        number = 0
    elif number > 255:
        number = 255

    binary_string = f"{number:08b}"

    for bit, pin in zip(binary_string, dac_bits):
        GPIO.output(pin, int(bit))


try:
    while True:
        try:
            voltage = float(input("Введите напряжение в Вольтах: "))
            number = voltage_to_number(voltage)
            number_to_dac(number)

        except ValueError:
            print("Вы ввели не число. Попробуйте ещё раз\n")

finally:
    GPIO.output(dac_bits, 0)
    GPIO.cleanup()