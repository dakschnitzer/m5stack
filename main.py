import epd1in54
from machine import SPI, Pin

# Initialize the SPI bus and the pins used by the display
spi = SPI(1)
cs = Pin(9)
dc = Pin(15)
rst = Pin(0)
busy = Pin(4)

# Create an instance of the epd1in54 class
epd = epd1in54.EPD(spi, cs, dc, rst, busy)

# Initialize the display
epd.init()

# Clear the display
epd.clear_frame_memory(0xFF)
epd.display_frame()

# Set the font and text color
epd.set_font(epd.FONT_DEFAULT)
epd.set_text_color(0)
epd.set_background_color(255)

# Draw "Hello World!" at position (20, 50)
epd.draw_string(20, 50, "Hello World!")

# Update the display
epd.display_frame()