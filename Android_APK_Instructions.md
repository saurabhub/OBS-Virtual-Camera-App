# Android App Installation Guide

I have written the complete source code for the Android Mock Camera app, including the UI and auto-permission logic. 

However, your computer does not currently have the `gradle` build tools installed in the command line path to compile this code into an `.apk` file directly.

## How to Build the App using Android Studio (Recommended)

To get this app onto your phone, follow these simple steps using Android Studio:

### 1. Open the Project
1. Open **Android Studio**.
2. Click on **Open**.
3. Navigate to and select this folder:
   `c:\Users\Saurabh Yadav\Desktop\Projects\OBS Camera\android_client`
4. Click **OK**.

### 2. Let Gradle Sync
Once opened, Android Studio will automatically download all the required Gradle dependencies (`com.android.tools.build:gradle`, `kotlin-gradle-plugin`, etc.). Wait for the progress bar at the bottom to finish.

### 3. Connect your Phone & Install
1. Connect your Realme phone to your computer via a USB cable.
2. Make sure **USB Debugging** is turned ON in Developer Options on your phone.
3. In Android Studio, your phone should appear in the top toolbar next to the green "Play" (Run) button.
4. Click the green **Run 'app'** button (Shift + F10).

This will compile the Kotlin code into an APK, install it on your phone, and launch the app. The app is fully programmed to ask for all necessary Camera and System Overlay permissions automatically upon first launch.

### 4. Build a shareable APK
If you want an `.apk` file to share with others:
1. In Android Studio, go to the top menu and select **Build > Build Bundle(s) / APK(s) > Build APK(s)**
2. Once done, a popup will appear at the bottom right. Click **Locate** to find your compiled `app-debug.apk` file.
