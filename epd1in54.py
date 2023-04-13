from machine import SPI, Pin
import utime as time
import esp32

# Display resolution
EPD_WIDTH       = 200
EPD_HEIGHT      = 200

# M5Stack CoreInk pins
# Initialize the SPI bus and the pins used by the display
spi = SPI(1)
CS_PIN = Pin(9)
DC_PIN = Pin(15)
RST_PIN = Pin(0)
BUSY_PIN = Pin(4)


class device:
    def __init__(self):
        import spidev
        import RPi.GPIO

        self.GPIO = RPi.GPIO
        self.SPI = spidev.SpiDev()
        
    def digital_write(pin, value):
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

#logger = logging.getLogger(__name__)

class EPD:
    def __init__(self):
        self.reset_pin = RST_PIN
        self.dc_pin = DC_PIN
        self.busy_pin = BUSY_PIN
        self.cs_pin = CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    lut_full_update = [
        0x02, 0x02, 0x01, 0x11, 0x12, 0x12, 0x22, 0x22, 
        0x66, 0x69, 0x69, 0x59, 0x58, 0x99, 0x99, 0x88, 
        0x00, 0x00, 0x00, 0x00, 0xF8, 0xB4, 0x13, 0x51, 
        0x35, 0x51, 0x51, 0x19, 0x01, 0x00
    ]

    lut_partial_update  = [
        0x10, 0x18, 0x18, 0x08, 0x18, 0x18, 0x08, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00, 0x13, 0x14, 0x44, 0x12, 
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
        
    # Hardware reset
    def reset(self):
        device.digital_write(self.reset_pin, 1)
        device.delay_ms(200) 
        device.digital_write(self.reset_pin, 0)         # module reset
        device.delay_ms(5)
        device.digital_write(self.reset_pin, 1)
        device.delay_ms(200)   

    def send_command(self, command):
        device.digital_write(self.dc_pin, 0)
        device.digital_write(self.cs_pin, 0)
        device.spi_writebyte([command])
        device.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        device.digital_write(self.dc_pin, 1)
        device.digital_write(self.cs_pin, 0)
        device.spi_writebyte([data])
        device.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
#        logger.debug("e-Paper busy")
        while(device.digital_read(self.busy_pin) == 1):      # 0: idle, 1: busy
            device.delay_ms(100)
#        logger.debug("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xC4)
        self.send_command(0x20) # MASTER_ACTIVATION
        self.send_command(0xFF) # TERMINATE_FRAME_READ_WRITE
        
        self.ReadBusy()

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start >> 3) & 0xFF)
        self.send_data((x_end >> 3) & 0xFF)
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x >> 3) & 0xFF)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        # self.ReadBusy()
        
    def init(self, lut):
        if (device.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        
        self.send_command(0x01) # DRIVER_OUTPUT_CONTROL
        self.send_data((EPD_HEIGHT - 1) & 0xFF)
        self.send_data(((EPD_HEIGHT - 1) >> 8) & 0xFF)
        self.send_data(0x00) # GD = 0 SM = 0 TB = 0
        
        self.send_command(0x0C) # BOOSTER_SOFT_START_CONTROL
        self.send_data(0xD7)
        self.send_data(0xD6)
        self.send_data(0x9D)
        
        self.send_command(0x2C) # WRITE_VCOM_REGISTER
        self.send_data(0xA8) # VCOM 7C
        
        self.send_command(0x3A) # SET_DUMMY_LINE_PERIOD
        self.send_data(0x1A) # 4 dummy lines per gate
        
        self.send_command(0x3B) # SET_GATE_TIME
        self.send_data(0x08) # 2us per line
        
        self.send_command(0x11) # DATA_ENTRY_MODE_SETTING
        self.send_data(0x03) # X increment Y increment
        
        # set the look-up table register
        self.send_command(0x32)
        for i in range(0, len(lut)):
            self.send_data(lut[i])
        # EPD hardware init end
        return 0

    def getbuffer(self, image):
        buf = [0xFF] * (int(self.width / 8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        if(imwidth == self.width and imheight == self.height):
#            logger.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
#            logger.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy*self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, image):
        if (image == None):
            return
            
        self.SetWindow(0, 0, self.width, self.height)
        for j in range(0, self.height):
            self.SetCursor(0, j)
            self.send_command(0x24)
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])   
        self.TurnOnDisplay()
        
    def Clear(self, color=0xFF):
        # self.SetWindow(0, 0, self.width - 1, self.height - 1)
        # send the color data
        self.SetWindow(0, 0, self.width, self.height)
        # epdconfig.digital_write(self.dc_pin, 1)
        # epdconfig.digital_write(self.cs_pin, 0)
        for j in range(0, self.height):
            self.SetCursor(0, j)
            self.send_command(0x24)
            for i in range(0, int(self.width / 8)):
                self.send_data(color)
        # epdconfig.digital_write(self.cs_pin, 1)
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP_MODE
        self.send_data(0x01)
        
        device.delay_ms(2000)
        device.module_exit()
### END OF FILE ###
