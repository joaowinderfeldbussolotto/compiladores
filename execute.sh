#!/bin/zsh

echo "Initializing..."

# python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Running..."

# python3 src/geradorafd.py ../inputs/entrada.txt
python3 src/compiladorok.py ../inputs/codigo.txt outputs/afd.csv

echo "Done!"

# echo "Cleaning..."
# rm -rf venv







# Path: execute.sh
