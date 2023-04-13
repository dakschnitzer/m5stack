import epd1in54




# Create an instance of the epd1in54 class
epd = epd1in54.EPD()

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