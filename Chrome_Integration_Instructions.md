# Chrome Integration & ADB Setup

To force Google Chrome (or other apps) to prioritize your Mocked Custom Camera over the physical device lens, follow these steps:

## Step 1: Grant Permissions via ADB
Since your app creates a virtual camera and uses `SYSTEM_ALERT_WINDOW` (Draw over other apps), grant the permissions aggressively via ADB to bypass any Android GUI limitations:
```bash
adb shell pm grant com.example.obscamera android.permission.CAMERA
adb shell appops set com.example.obscamera SYSTEM_ALERT_WINDOW allow
```

## Step 2: Virtual/External Camera Mocking
In modern Android versions (Android 11+), injecting a fake system camera without ROOT or Xposed/LSPosed is generally restricted by the OS. However, utilizing the `android.hardware.camera.external` feature tells the OS to treat your app's `VirtualDisplay` and `Surface` endpoints as a UVC (USB Video Class) equivalent.

If you are using Chrome on Android:
1. Open Chrome and go to `chrome://flags`
2. Search for **"Override software rendering list"** and enable it.
3. This often forces Chrome to expose alternative MediaProjection outputs as camera inputs.

For a pure software mock, you may need to rely on Android's `MediaProjection` API. Your app captures a hidden Surface (where we decode our OBS UDP frames to) and shares it with the system as a Virtual Display. When Chrome invokes `navigator.mediaDevices.getUserMedia()`, testing environments and specific app bridges allow this Virtual Display to appear in the device enumerated list.

## Step 3: Network & Lag Optimizations
Keep the Latency low:
1. Ensure your PC running OBS and Android phone are on the same 5GHz WiFi network.
2. If delays occur, in `obs_udp_sender.py`, lower `cv2.IMWRITE_JPEG_QUALITY` from `70` to `50` or `40`.
3. Tweak the frame-resizing: Drop down to `(854, 480)` inside the python script instead of `(1280, 720)` if the network cannot sustain UDP packets efficiently.
