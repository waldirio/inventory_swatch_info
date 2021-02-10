# inventory_swatch_info
Script to collect the inventory from cloud.redhat.com and run against the information on subscription watch.


# Help
~~~
#./inventory_swatch_info.py -h
Usage: inventory_swatch_info.py [options]

Options:
  -h, --help            show this help message and exit
  -l LOGIN, --login=LOGIN
                        Login user
  -f FILENAME, --filename=FILENAME
                        Login user
  -p PASSWORD, --password=PASSWORD
                        Password for specified user. Will prompt if omitted
  -s SERVER, --server=SERVER
                        FQDN of server - omit https://
  -v, --verbose         Verbose output
  -d, --debug           Debugging output (debug output enables verbose)
~~~


# Example output
~~~
$ cat insights_swatch_match-<customer_login_here>.csv
id,server,reporter,arch,core_per_sockets,infrastructure.type,number_of_cpus,number_of_socket,satellite_managed,subscription_status,satellite_id,hypervisor,sw_inventory_id,sw_cores,sw_display_name,sw_hardware_type,sw_inventory_id,sw_last_seen,sw_measurement_type,sw_number_of_guests,sw_sockets,sw_subscription_manager_id
...
~~~


# How to implement this script

How to implement this script.

Fedora 33:

- Install python 2.7 and git
~~~
[user1@fedoraxfce ~]$ sudo dnf install python2.7 git -y
~~~
- Install virtualenv
~~~
[user1@fedoraxfce ~]$ pip install virtualenv
~~~
- Create a new virtual environment using python 2.7
~~~
[user1@fedoraxfce ~]$ virtualenv -p /usr/bin/python2.7 /tmp/.virtualenv/inventory_swatch
~~~
- Clone the project and change to the directory
~~~
[user1@fedoraxfce ~]$ git clone https://github.com/waldirio/inventory_swatch_info.git
[user1@fedoraxfce ~]$ cd inventory_swatch_info
~~~
- Load it
~~~
[user1@fedoraxfce inventory_swatch_info]$ source /tmp/.virtualenv/inventory_swatch/bin/activate
~~~
- Install requirements
~~~
(inventory_swatch) [user1@fedoraxfce inventory_swatch_info]$ pip install -r requirements
~~~
- Use it
~~~
./inventory-swatch_info.py
~~~
or 
~~~
./inventory-swatch_info.py -v -l 'username' -p 'password'
~~~
