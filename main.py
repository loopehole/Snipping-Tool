from PIL import ImageGrab
import time

# Function to capture the screen
def capture_screen():   
    time.sleep(2)  # Wait for 2 seconds -> (to give you time to switch windows if needed)
    
    screenshot = ImageGrab.grab() # for Capturing the screenshot

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"screenshot_{timestamp}.png" # Generate a unique filename using the current timestamp

    screenshot.save(filename)  # Save the screenshot with the unique filename

    print(f"Screenshot saved as '{filename}'")

capture_screen()
