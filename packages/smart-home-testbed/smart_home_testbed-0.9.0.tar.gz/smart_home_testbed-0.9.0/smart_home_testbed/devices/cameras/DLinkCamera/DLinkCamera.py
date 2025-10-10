import time
from ....DeviceState import CameraScreenshotState
from ....DeviceControl import CameraErrorControl


class DLinkCamera(CameraScreenshotState, CameraErrorControl):
    """
    DLink camera (DCS-8000LH).
    """

    ### Class attributes
    # Android package
    android_package = "com.dlink.mydlinkunified"
    # SSIM threshold below which images are considered different
    SSIM_DIFF_THRESHOLD = 0.9
    ## Screen coordinates
    # Stream event
    x_start = 637
    y_start = 1479
    x_stop = 76
    y_stop = 1648
    # Rate prompt
    x_rate = 324
    y_rate = 1357
    # Error message
    x_error = 540
    y_error = 1333


    def start_app(self) -> None:
        """
        Start the `mydlink` app on the phone,
        and potentially dismiss the rate prompt.
        This method overwrites the method from the parent class DeviceControl.

        Raises:
            IndexError: If no adb device is found.
        """
        phone = self.get_phone()
        # Launch app
        phone.shell(f"monkey -p {self.android_package} -c android.intent.category.LAUNCHER 1")
        time.sleep(10)
        # Dismiss rate prompt
        phone.shell(f"input tap {self.x_rate} {self.y_rate}")
        del phone
