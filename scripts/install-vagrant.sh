#!/bin/bash
# required on ubuntu 14.04
sudo apt-get install -y python3.4-venv

# make a virtualenv and activate it 
mkdir -p ~/venv
python3 -m venv ~/venv
source ~/venv/bin/activate

# make a project dir
mkdir -p ~/project
cd ~/project

# add virtualenv to shells
echo 'source ~/venv/bin/activate' >> ~/.bashrc 

