import math
import random
import cv2
from skimage.metrics import structural_similarity as ssim
from ....DeviceState import ScreenshotState
from ....DeviceControl import TuyaControl, LightControl


class TuyaLight(ScreenshotState, TuyaControl, LightControl):
    """
    Generic Tuya light bulb.
    """

    # Default filename for the OFF screenshot
    FILENAME_SCREENSHOT_OFF = "off.png"
    # SSIM thresholds
    SSIM_DIFF_THRESHOLD = 0.999     # State change
    OFF_SSIM_DIFF_THRESHOLD = 0.95  # Check if light is off

    ### Screen coordinates
    # Device controls
    device_x = 648
    device_y = 945
    ## Events
    # Toggle
    x = 540
    y = 2206
    # Brightness
    x_left_gauge  = 216
    x_right_gauge = 864
    y_brightness  = 1576
    # Color
    x_color_tab    = 540
    y_color_tab    = 364
    x_color_center = 540
    y_color_center = 1042
    y_color_ring   = 727


    def __init__(self, ipv4: str, **kwargs) -> None:
        """
        Constructor.
        Initializes the Tuya light bulb with its IP address,
        and computes the grayscale array of the bulb's OFF screenshot.

        Args:
            ipv4 (str): IP address of the Tuya light bulb.
            kwargs (dict): device-specific additional parameters,
                           including the path to the OFF screenshot.
        """
        # Call parent constructor
        super().__init__(ipv4, **kwargs)

        # Compute gray array of off screenshot
        image_off = cv2.imread(kwargs.get("path_screenshot_off", TuyaLight.FILENAME_SCREENSHOT_OFF))
        self.image_off_gray = cv2.cvtColor(image_off, cv2.COLOR_BGR2GRAY)
    

    def do_set_color(self) -> None:
        """
        Randomly set the color of the Tuya light.
        """
        # Retrieve the phone instance
        phone = self.get_phone()

        # Ensure the color tab is selected
        phone.shell(f"input tap {self.x_color_tab} {self.y_color_tab}")

        # Generate random position on the color ring
        radius = self.y_color_center - self.y_color_ring
        angle_deg = random.randint(0, 360)
        angle_rad = angle_deg * math.pi / 180
        x = self.x_color_center + radius * math.cos(angle_rad)
        y = self.y_color_center + radius * math.sin(angle_rad)
        
        # Set the color
        phone.shell(f"input tap {x} {y}")
    

    def is_off(self):
        """
        Check if the light is off.
        """
        # Take screenshot and convert to grayscale
        state = self.get_state()
        screenshot_gray = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY)

        # Compute SSIM with OFF screenshot
        try:
            score = ssim(self.image_off_gray, screenshot_gray, full=False)
            return score > self.OFF_SSIM_DIFF_THRESHOLD
        except ValueError:
            return False
