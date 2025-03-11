# Two-Way-ANNOVA
Statistical Analysis Model for Evaluating the Effect of Gender and Age on Academic Performance Using Two-Way ANOVA


https://console.cloud.google.com/

sudo apt update && sudo apt upgrade && clear

git clone https://github.com/JV-Vigneesh/Two-Way-ANNOVA

cd Two-Way-ANNOVA

sudo apt install python3-pip

pip install -r requirements.txt

sudo apt-get install -y docker.io

sudo docker build . -t sm

sudo docker run -p 8003:8003 sm
