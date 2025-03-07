
@echo off
echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Setup completed! Run the following commands to start:
echo venv\Scripts\activate
echo uvicorn main:app --reload