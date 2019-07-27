# Item Catalog- A RESTful multi-user webapp

## Installation

### Install VirtualBox

VirtualBox is the software that actually runs the virtual machine. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) Install the _platform package_ for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.

### Install Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. [Download it from vagrantup.com.](https://www.vagrantup.com/downloads.html) Install the version for your operating system.

**Windows users:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

![vagrant --version](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/584881ee_screen-shot-2016-12-07-at-13.40.43/screen-shot-2016-12-07-at-13.40.43.png)

_If Vagrant is successfully installed, you will be able to run_ `vagrant --version`
_in your terminal to see the version number._
_The shell prompt in your terminal may differ. Here, the_ `$` _sign is the shell prompt._

### Download the VM configuration

Use Github to fork and clone, or download, the repository.

You will end up with a new directory called item-catalog. Change to this directory in your terminal with `cd`.



## Instructions

Navigate to the `item-catalog/vagrant/catalog` directory in a terminal.

Type `vagrant up; vagrant ssh` into the terminal and press Return. Wait for the prompt in the Ubuntu VM that's loaded in the terminal.

Type `cd /vagrant/catalog/` and type return to navigate to the item catalog directory inside the vagrant environment.

run database_setup.py to create the database: 
`python database_setup.py`

`sudo bash cat_config.sh`
 to populate the database, then

`python application.py`.

Finally, navigate to `localhost:8000` in your browser.
