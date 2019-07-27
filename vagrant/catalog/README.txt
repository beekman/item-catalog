To run this project

Navigate to the item-catalog/vagrant/catalog directory in a terminal.

Type "vagrant up; vagrant ssh" into the terminal and press Return. Wait for the prompt in the Ubuntu VM that's loaded in the terminal.

Type "cd /vagrant/catalog/" and type return to navigate to the item catalog directory inside the vagrant environment.

run database_setup.py to create the database: python3 database_setup.py

sudo bash cat_config.sh
 to populate the database

run application.py and navigate to localhost:8000 in your browser
