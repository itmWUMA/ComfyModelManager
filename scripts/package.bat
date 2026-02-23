@echo off
setlocal

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

pyinstaller --onefile --name ComfyModelManager --noconsole --icon resources\icon.png main.py

echo.
echo Build complete. Output: dist\ComfyModelManager.exe
endlocal
