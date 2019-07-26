apt-get -qqy update
DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
apt-get install python3-setuptools
easy_install3 pip
python3 pip install --upgrade pip
pip install -r requirements.txt
