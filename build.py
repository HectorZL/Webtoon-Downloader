import PyInstaller.__main__
import os
import shutil

# Executable name
EXE_NAME = "WebtoonDownloaderGUI"
SCRIPT_PATH = "gui.py"

def build():
    print(f"Starting build for {EXE_NAME}...")
    
    # Path to customtkinter
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    
    params = [
        SCRIPT_PATH,
        '--noconsole',
        '--onefile',
        f'--name={EXE_NAME}',
        # Include customtkinter themes/assets
        f'--add-data={ctk_path};customtkinter/',
        '--clean',
        '--workpath=build',
        '--distpath=dist',
        '--specpath=.'
    ]
    
    PyInstaller.__main__.run(params)
    print("Build finished. Check the 'dist' folder.")

if __name__ == "__main__":
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    build()
