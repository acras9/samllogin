#!/bin/bash
echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup completed! Run the following commands to start:"
echo "source venv/bin/activate"
echo "uvicorn main:app --reload"
