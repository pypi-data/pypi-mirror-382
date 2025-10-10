import time
from ....DeviceState import CameraScreenshotState
from ....DeviceControl import CameraControl, SmartThingsControl


class TapoCameraSmartThings(CameraScreenshotState, CameraControl, SmartThingsControl):
    """
    Tapo camera (C200),
    controlled through the SmartThings app.
    """

    ### Class attributes
    # SSIM threshold below which images are considered different
    SSIM_DIFF_THRESHOLD = 0.98
    ## Screen coordinates
    # Start stream (device controls button)
    x_start = 281
    y_start = 1454
    # Stop stream (return button)
    x_stop = 76
    y_stop = 267


    def start_app(self) -> None:
        """
        Start the SmartThings app on the phone,
        and switch to the "Devices" tab.
        DO NOT open the device controls.

        Raises:
            IndexError: If no adb device is found.
        """
        phone = self.get_phone()
        # Start SmartThings app
        phone.shell(f"monkey -p {SmartThingsControl.android_package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        # Open "Devices" tab
        phone.shell(f"input tap {SmartThingsControl.devices_x} {SmartThingsControl.devices_y}")
