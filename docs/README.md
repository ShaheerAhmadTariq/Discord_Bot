# Bot setup guide
## Download Miniconda
mkdir -p ./miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ./miniconda3/miniconda.sh
bash ./miniconda3/miniconda.sh -b -u -p ./miniconda3
rm -rf /miniconda3/miniconda.sh
./miniconda3/bin/conda init bash
## close the terminal and open a new one


## Create a new Conda environment 
conda create -n textgen python=3.10.9
conda activate textgen


## Upload bot zip file
apt update
apt install unzip 
unzip Discord_Bot-staging.zip
cd Discord_Bot-staging
pip install -r requirements.txt

## Starting Pygmalion
source miniconda3/bin/activate
conda activate textgen
mkdir models
./start.bash

## open a new terminal 
source miniconda3/bin/activate
conda activate textgen
./startbot.bash
