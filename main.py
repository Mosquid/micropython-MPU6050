from machine import I2C, Pin
import math
import time

# Constants for the device I2C address and registers
MPU6050_ADDR = 0x68
ACCEL_XOUT_H = 0x3B
ACCEL_ZOUT_H = 0x3F

led_degree = 25
led_pins = [21, 20, 19, 18]  # Change these as per your GPIO pin connections
leds = [Pin(pin, Pin.OUT) for pin in led_pins]
scl = Pin(27)
sda = Pin(26)

# Function to read two bytes and convert to a signed number
def read_2_bytes(i2c, addr, reg):
    high, low = i2c.readfrom_mem(addr, reg, 2)
    value = (high << 8) + low
    if value >= 0x8000:
        return -((65535 - value) + 1)
    else:
        return value

# Function to calculate the roll angle
def calculate_roll(x, z):
    radians = math.atan2(x, z)
    return math.degrees(radians)

# Set up I2C using correct SDA and SCL pins
i2c = I2C(1, scl=scl, sda=sda, freq=400000)  # Adjust pins as necessary

# Initialize MPU6050
i2c.writeto_mem(MPU6050_ADDR, MPU6050_ADDR, b'\x00')  # Wake up sensor

def get_roll_percentage(roll):
    max = led_degree * 2
    roll = roll + led_degree
    
    return (roll / max) * 100

def update_leds(roll):
    # Turn all LEDs off initially
    for led in leds:
        led.off()

    last_index = len(leds) - 1
    percentage = get_roll_percentage(roll)

    if percentage < 0:
        leds[0].on()
    elif percentage > 100:
        leds[last_index].on()
    else:
        index = round(percentage / 100 * last_index)
        leds[index].on()

# Main loop to read and print tilt angle
while True:
    accel_x = read_2_bytes(i2c, MPU6050_ADDR, ACCEL_XOUT_H)
    accel_z = read_2_bytes(i2c, MPU6050_ADDR, ACCEL_ZOUT_H)

    roll = calculate_roll(accel_x, accel_z)
    update_leds(roll)

    time.sleep(.1)
