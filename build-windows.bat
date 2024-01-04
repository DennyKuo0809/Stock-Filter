pip install -r requirements.txt
pip install pyinstaller
pyinstaller -y --clean --name stock.exe --hidden-import=requirements.txt api_server.py --onefile
copy dist\stock.exe .\stock.exe
