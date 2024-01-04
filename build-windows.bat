python3 -m pip install requirements.txt
pyinstaller -y --clean --name stock.exe --hidden-import=Import.txt api_server.py --onefile
copy dist\stock.exe ./