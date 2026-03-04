import os
import PyInstaller.__main__
import customtkinter

# Find where the customtkinter library is installed to bundle its assets (themes/fonts)
ctk_path = os.path.dirname(customtkinter.__file__)

print("====================================")
print("Building OBS_Camera_Sender.exe...")
print(f" bundling UI assets from: {ctk_path}")
print("====================================")

PyInstaller.__main__.run([
    'standalone_sender.py',
    '--noconfirm',
    '--windowed',
    '--onedir',
    '--name=OBS_Camera_Sender_GUI',
    f'--add-data={ctk_path};customtkinter/'
])

print("\n\nBuild Complete successfully!")
print("Your .exe is located in the 'dist/OBS_Camera_Sender_GUI' directory.")
