#!/bin/bash

set -e

echo -e "\n\033[1;34m==> Creating and activating Python virtual environment...\033[0m"

if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo -e "\033[1;32mVirtual environment created in ./venv\033[0m"
else
  echo -e "\033[1;33mVirtual environment already exists\033[0m"
fi

# Activate venv
source venv/bin/activate

echo -e "\n\033[1;34m==> Upgrading pip...\033[0m"
pip install --upgrade pip

echo -e "\n\033[1;34m==> Installing dependencies...\033[0m"
pip install gitpython rich prompt_toolkit

echo -e "\n\033[1;32m==> Setup complete! Virtual environment is activated.\033[0m"
echo -e "To activate it later, run: \033[1;36msource venv/bin/activate\033[0m\n"
