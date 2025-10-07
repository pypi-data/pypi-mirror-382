# pyajazz (Ajazz AKP HID Controller)
Python module for interfacing with Ajazz AKP devices (such as the AKP153E Desk Controller), enabling programmatic control over button images, callbacks, and device states.

## Table of Contents
- [Installation](#installation)
- [Overview](#overview)
- [Features](#features)
- [Supported Device Capabilities](#supported-device-capabilities)
- [Usage](#usage)
  - [Sample Code](#sample-code)
  - [Setting and Clearing Button Images](#setting-and-clearing-button-images)
  - [Configuring Button Actions](#configuring-button-actions-callbacks)
  - [Sleep Mode](#sleep-mode)
  - [Brightness Control](#brightness-control)
  - [Setting Logo Image](#setting-logo-image)

## Installation
```bash
pip install pyajazz
# or
git clone https://github.com/superdeee/pyajazz
cd pyajazz
pip install .
```
⚠️ **Note:** This package relies on `hidapi`. You may need to install OS-specific dependencies before installing `cython-hidapi`. Refer to the [cython-hidapi README](https://github.com/trezor/cython-hidapi?tab=readme-ov-file#cython-hidapi) for details.

## Overview
This module provides an easy-to-use Python interface for controlling Ajazz AKP Devices. `pyajazz` module is primarily designed for the AKP153E Desk Controller. However, other models such as the AKP05, AKP03, and similar rebranded devices may also work (untested). The module handles all necessary requests, allowing full use of the device without relying on the Chinese OEM software.

❗ **Read the usage section carefully to avoid bricking your device!**

## Features
- 🧠 Thread-safe read/write handling
- 🧾 Queue-based events handling
- 🔧 Easy event callbacks configuration
- 🧯 Error handling
- 🧰 Context-managed connection lifecycle

## Supported Device Capabilities
- Device state:
    - Initialize / Shut down
    - Sleep / Wake up
- Set screen brightness
- Set/Clear individual icon slots
- Clear the whole screen
- Set shutdown logo
- Button press/release callbacks

## Usage
### Sample Code
```python
from pyajazz import Device

jpeg_img_data = ... # load JPEG data from file or create image programmatically

with Device() as device:
    device.on_press(position=1, callback=lambda: print("Hello world!"))
    device.set_button_image(position=1, data=jpeg_img_data)

    while True:
        device.handle_pending_inputs()

```

### Setting and Clearing Button Images

When setting button images, JPEG-encoded data must be provided via the data parameter. Images should have dimensions that are multiples of 16 (e.g., 16×N x 16×M) and contain minimal metadata. Ensure metadata is stripped to prevent issues, including possible device bricking. Attempting to set a logo image with extensive metadata (e.g., EXIF) may cause the device to become unresponsive. Always sanitize image files before sending. Images wider/longer than 96 pixels will overflow to adjacent buttons areas.

Note: The AKP153 display controller expects the screen to be rotated 90° clockwise relative to its physical orientation. Therefore, images must be rotated 90° counter-clockwise before sending to the device.

Each screen/button area is referred to as a **position**, numbered 1–18. The layout for AKP153 device is as follows:

```
+------+------+------+------+------+----+
|  13  |  10  |  7   |  4   |  1   | 16 |
+------+------+------+------+------+----+
|  14  |  11  |  8   |  5   |  2   | 17 |
+------+------+------+------+------+----+
|  15  |  12  |  9   |  6   |  3   | 18 |
+------+------+------+------+------+----+
```

**Tip:** *Reading and encoding the images with opencv is a nice way of removing unnecessary metadata*
```python
image_data = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
```

#### Setting Image
**`set_button_image(position, data)`**
- `position` (int): ID of the screen area (1–18)
- `data` (bytes | bytearray | list[int]): JPEG-encoded image (max ~10kB, no metadata)

#### Clearing Image
**`clear_button_image(position)`**
- `position` (int): ID of the screen area (1-18)

#### Clear All Images
**`clear_all()`**

### Configuring Button Actions (Callbacks)

The Ajazz AKP153 supports two types of button events - press and release - which can be configured independently. The device does not support key combinations.

#### Setting Button Press Callback
**`on_press(position, callback)`**
- `position` (int): ID of the button (1-15)
- `callback` (Callable): callable to run on press event

#### Setting Button Release Callback
**`on_release(position, callback)`**
- `position` (int): ID of the button (1-15)
- `callback` (Callable): callable to run on release event

#### Remove Callbacks
**`clear_callbacks(position)`**
- `position` (Optional[int] = None): ID of the button (1-15) or None (clears all button callbacks)

### Sleep Mode

The device supports sleep mode in which it handles any USB input requests (button images can be set while asleep). The first user interaction after entering the sleep mode wakes it up, but is not populated to the controlling software.

#### Entering Sleep Mode
**`sleep()`**

#### Waking Up (through software)
**`wakeup()`**

### Brightness Control
**`set_brightness(brightness)`**
- `brightness` (int): brightness level (0-100)

### Setting Logo Image
While not connected to any software Ajazz devices display a logo which can be changed with the command below. Note that the display's physical resolution is 854x480, but due to the device's rotation, logo images must be 480x854 (portrait orientation). **Make sure any redundant image metadata, such as EXIF, is removed prior to sending!**

**`set_logo_image(data)`**
- `data` (bytes | bytearray | list[int]): JPEG encoded image data with no metadata (512kB maximum)

Logo image can be sanitized with OpenCV using a following snippet:
```python
def prep_logo(path):
    logo_img = cv2.imread(path)
    if logo_img is None:
        raise FileNotFoundError(f"Can't open: {path}")

    if logo_img.shape[0] < logo_img.shape[1]:
        logo_img = cv2.rotate(logo_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    if logo_img.shape != (854, 480, 3):
        print("Logo image resolution must be 854x480, resizing...")
        logo_img = cv2.resize(logo_img, (480, 854))

    success, encoded_image = cv2.imencode('.jpg', logo_img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    if not success:
        raise ValueError("Can't encode as JPEG.")
    
    return encoded_image
```