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
$ cat insights_swatch_match.csv
id,server,reporter,arch,core_per_sockets,infrastructure.type,number_of_cpus,number_of_socket,satellite_managed,subscription_status,satellite_id,hypervisor,sw_inventory_id,sw_cores,sw_display_name,sw_hardware_type,sw_inventory_id,sw_last_seen,sw_measurement_type,sw_number_of_guests,sw_sockets,sw_subscription_manager_id
...
~~~


# How to implement this script
- Clone the project
~~~
# git clone https://github.com/waldirio/inventory_swatch_info.git
# cd inventory_swatch_info
~~~
- Create a new virtual environment using python 2.7
~~~
# python2.7 -m virtualenv /tmp/.virtualenv/inventory_swatch_info
~~~
- Load it
~~~
$ source /tmp/.virtualenv/inventory_swatch_info/bin/activate
(inventory_swatch_info) $
~~~
- Install the requirements
~~~
(inventory_swatch_info) $ pip install -r requirements 
~~~
- Uset it.
~~~
./inventory_swatch_info.py
~~~
or
~~~
./inventory_swatch_info.py -v -l `username` -p `password`
~~~
