import utime as time

# Pin definition for ESP32-WROVER
RST_PIN = 0
DC_PIN = 15
CS_PIN = 9
BUSY_PIN = 4

def __init__(self):
    import spidev
    import RPi.GPIO

    self.GPIO = RPi.GPIO
    self.SPI = spidev.SpiDev()

def digital_write(self, pin, value):
    self.GPIO.output(pin, value)

def digital_read(self, pin):
    return self.GPIO.input(pin)

def delay_ms(self, delaytime):
    time.sleep(delaytime / 1000.0)

def spi_writebyte(self, data):
    self.SPI.writebytes(data)

def spi_writebyte2(self, data):
    self.SPI.writebytes2(data)

def module_init(self):
    self.GPIO.setmode(self.GPIO.BCM)
    self.GPIO.setwarnings(False)
    self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
    self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
    self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
    self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)

    # SPI device, bus = 0, device = 0
    self.SPI.open(0, 0)
    self.SPI.max_speed_hz = 4000000
    self.SPI.mode = 0b00
    return 0

def module_exit(self):
#    logger.debug("spi end")
    self.SPI.close()

#    logger.debug("close 5V, Module enters 0 power consumption ...")
    self.GPIO.output(self.RST_PIN, 0)
    self.GPIO.output(self.DC_PIN, 0)

    self.GPIO.cleanup([self.RST_PIN, self.DC_PIN, self.CS_PIN, self.BUSY_PIN])