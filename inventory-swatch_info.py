#!/usr/bin/env python
"""
# File: inventory_swatch_info.py
# Author: Waldirio M Pinheiro <waldirio@gmail.com>
# Contributor: Rich Jerrido <rjerrido@outsidaz.org>
# Purpose:
#   This script will collect the information from cloud.redhat.com/Inventory and
#   will put in a nice/simple view the whole information, being easy to create a
#   pivot table and moving on.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
"""

import getpass
import json
import urllib2
import urllib
import sys
import csv
from optparse import OptionParser
import requests

# ##### Insights Inventory
hypervisor_guests_list = []
hypervisor_guests_final = []
final_list = []
complete_list = []
stage_lst = []
# #####

# ##### Inventory & SubsWatch lists
inventory_list = []
systemdata = []
inv_swatch_list = []
complete_dataset_list = []
# #####

stage1_lst = ["id",
              "server",
              "reporter",
              "arch",
              "core_per_sockets",
              "infrastructure.type",
              "number_of_cpus",
              "number_of_socket",
              "satellite_managed",
              "subscription_status",
              "satellite_id",
              "hypervisor"]

complete_list.append(stage1_lst)
stage1_lst = []


def process_info(login, password, server):
    """
    Function responsible for collect and process the main info regarding
    to the Content Hosts on cloud.redhat.com
    """

    if options.debug:
        DEBUG = True
        VERBOSE = True
        print "[%sDEBUG%s] LOGIN -> %s " % (error_colors.OKBLUE, error_colors.ENDC, login)
        print "[%sDEBUG%s] PASSWORD -> %s " % (error_colors.OKBLUE, error_colors.ENDC, password)
        print "[%sDEBUG%s] SERVER -> %s " % (error_colors.OKBLUE, error_colors.ENDC, server)
    else:
        DEBUG = False
        VERBOSE = False

    if options.verbose:
        VERBOSE = True

    if DEBUG and not FILEINPUTMODE:
        outputfile = open(("cloud.redhat.com_output-%s.json" % login), "w")

    systemdata = []
    if FILEINPUTMODE:
        f = open(FILENAME, "r")
        jsondata = json.load(f)
        # systemdata = jsondata['results']
        systemdata = jsondata
    else:
        try:
            url = 'https://' + server + '/api/inventory/v1/hosts'
            if VERBOSE:
                print "=" * 80
                print "[%sVERBOSE%s] Connecting to -> %s " % (error_colors.OKGREEN, error_colors.ENDC, url)
            result = requests.get(url, auth=(login, password)).content
            jsonresult = json.loads(result)

            if VERBOSE:
                print
                "=" * 80
        except urllib2.URLError, e:
            print
            "Error: cannot connect to the API: %s" % (e)
            print
            "Check your URL & try to login using the same user/pass via the WebUI and check the error!"
            sys.exit(1)
        except Exception, e:
            print
            "FATAL Error - %s" % (e)
            sys.exit(2)

        try:
            page = 0
            per_page = 100
            # For debugging purposes
            # per_page = 5
            while (page == 0 or int(jsonresult['per_page']) == len(jsonresult['results'])):
            # For debugging purposes
            # while (page < 2):
                page += 1
                q = [('page', page), ('per_page', per_page)]
                url = "https://cloud.redhat.com/api/inventory/v1/hosts?" + urllib.urlencode(q)
                if VERBOSE:
                    print "=" * 80
                    print "[%sVERBOSE%s] Connecting to -> %s " % (error_colors.OKGREEN, error_colors.ENDC, url)
                result = requests.get(url, auth=(login, password)).content
                jsonresult = json.loads(result)
                systemdata += jsonresult['results']
            if DEBUG:
                with open('cloud.redhat.com_output-%s.json' % login, 'w') as json_file:
                    json.dump(systemdata, json_file)

        except Exception, e:
            print "FATAL Error - %s" % (e)
            sys.exit(2)

    if DEBUG and not FILEINPUTMODE:
        outputfile.close()

    for system in systemdata:
        print "%s Reported by -> %s" % (system['display_name'], system['reporter'])
        display_name = system['display_name']
        reporter = system['reporter']
        satellite_id = system['satellite_id']

        system_profile(system['id'], display_name, reporter, satellite_id)


def system_profile(id, display_name, reporter, satellite_id):
    """
    Function responsible for collect the system_profile of each Content Host
    hosted on cloud.redhat.com
    """
    global stage_lst

    url = 'https://' + server + '/api/inventory/v1/hosts/' + id + '/system_profile'

    result = requests.get(url, auth=(login, password)).content
    jsonresult = json.loads(result)

    stage_lst.append(id)
    stage_lst.append(display_name)
    stage_lst.append(reporter)

    try:
        arch = jsonresult['results'][0]['system_profile']['arch']
        stage_lst.append(arch)
    except KeyError:
        stage_lst.append("no arch key")

    try:
        cores_per_socket = jsonresult['results'][0]['system_profile']['cores_per_socket']
        stage_lst.append(cores_per_socket)
    except KeyError:
        stage_lst.append("no cores per socket key")

    try:
        infrastructure_type = jsonresult['results'][0]['system_profile']['infrastructure_type']
        stage_lst.append(infrastructure_type)
    except KeyError:
        stage_lst.append("no infrastructure_type key")

    try:
        number_of_cpus = jsonresult['results'][0]['system_profile']['number_of_cpus']
        stage_lst.append(number_of_cpus)
    except KeyError:
        stage_lst.append("no number of cpus key")

    try:
        number_of_sockets = jsonresult['results'][0]['system_profile']['number_of_sockets']
        stage_lst.append(number_of_sockets)
    except KeyError:
        stage_lst.append("no number of sockets key")

    try:
        satellite_managed = jsonresult['results'][0]['system_profile']['satellite_managed']
        stage_lst.append(satellite_managed)
    except KeyError:
        stage_lst.append("no satellite managed key")

    try:
        subscription_status = jsonresult['results'][0]['system_profile']['subscription_status']
        stage_lst.append(subscription_status)
    except KeyError:
        stage_lst.append("no subscription status key")

    stage_lst.append(satellite_id)

    final_list.append(stage_lst)
    stage_lst = []


def hypervisor_guests():
    """
    Function responsible to identify all the hypervisors "virt-who-" and then
    compare the full list against the hypervisor list. The main idea is to map
    which Content Host is running on top of which hypervisor.
    """
    global hypervisor_guests_list
    global complete_list

    # Filtering the CH with virt-who in the name
    stage_lst = []
    for ch in final_list:
        if 'virt-who-' in ch[1]:
            stage_lst.append(ch[1])
            stage_lst.append(ch[10])
            hypervisor_guests_list.append(stage_lst)
            stage_lst = []

    # Running on the list of virt-who-* servers to retrieve the guest list
    stage_lst = []
    for hyper in hypervisor_guests_list:

        url = 'https://' + server + '/api/rhsm-subscriptions/v1/hosts/' + hyper[1] + '/guests?limit=100&offset=0'

        result = requests.get(url, auth=(login, password)).content
        jsonresult = json.loads(result)

        if jsonresult['data']:
            for srv in jsonresult['data']:
                stage_lst.append(srv['display_name'])
                stage_lst.append(srv['inventory_id'])
                stage_lst.append(hyper[0])
                hypervisor_guests_final.append(stage_lst)
                stage_lst = []

    # Checking the complete inventory against the known ch/hypervisors
    stage_lst = []
    for each_ch in final_list:
        count = 0
        if (len(hypervisor_guests_final) > 0):
            for mapped_ch in hypervisor_guests_final:
                if (each_ch[0] == mapped_ch[1]):
                    count += 1
                    stage_lst.append(each_ch[0])
                    stage_lst.append(each_ch[1])
                    stage_lst.append(each_ch[2])
                    stage_lst.append(each_ch[3])
                    stage_lst.append(each_ch[4])
                    stage_lst.append(each_ch[5])
                    stage_lst.append(each_ch[6])
                    stage_lst.append(each_ch[7])
                    stage_lst.append(each_ch[8])
                    stage_lst.append(each_ch[9])
                    stage_lst.append(each_ch[10])
                    stage_lst.append(mapped_ch[2])

            if (count == 1):
                complete_list.append(stage_lst)
                stage_lst = []
            elif (count == 0):
                stage_lst.append(each_ch[0])
                stage_lst.append(each_ch[1])
                stage_lst.append(each_ch[2])
                stage_lst.append(each_ch[3])
                stage_lst.append(each_ch[4])
                stage_lst.append(each_ch[5])
                stage_lst.append(each_ch[6])
                stage_lst.append(each_ch[7])
                stage_lst.append(each_ch[8])
                stage_lst.append(each_ch[9])
                stage_lst.append(each_ch[10])
                stage_lst.append("No hypervisor")
                complete_list.append(stage_lst)
                stage_lst = []

        else:
            stage_lst.append(each_ch[0])
            stage_lst.append(each_ch[1])
            stage_lst.append(each_ch[2])
            stage_lst.append(each_ch[3])
            stage_lst.append(each_ch[4])
            stage_lst.append(each_ch[5])
            stage_lst.append(each_ch[6])
            stage_lst.append(each_ch[7])
            stage_lst.append(each_ch[8])
            stage_lst.append(each_ch[9])
            stage_lst.append(each_ch[10])
            stage_lst.append("No hypervisor")
            complete_list.append(stage_lst)
            stage_lst = []


def csv_export():
    """
    Function that will generate the final csv file.
    """
    with open('compact_version-%s.csv' % login, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)

        for rows in complete_list:
            csv_writer.writerow(rows)

        print "The file compact_version-{}.csv was created!".format(login)



def process_info_swatch(login, password, server):
    """
    Function responsible for collect and process the main info regarding
    to the Content Hosts on cloud.redhat.com
    """

    global systemdata
    global complete_dataset_list

    with open('compact_version-%s.csv' % login, 'r') as fp:
        csv_reader = csv.reader(fp, delimiter = ',')
        stage_lst = []
        for row in csv_reader:
            print row
            if row[0] == "id":
                print "first line"
                stage_lst = row
                aux = ['sw_inventory_id','sw_cores','sw_display_name','sw_hardware_type','sw_inventory_id','sw_last_seen','sw_measurement_type','sw_number_of_guests','sw_sockets','sw_subscription_manager_id']
                stage_lst = stage_lst + aux
                complete_dataset_list.append(stage_lst)
            else:
                print row
                inventory_list.append(row)

    
    try:
        url = 'https://' + server + '/api/rhsm-subscriptions/v1/hosts/products/RHEL?limit=100&offset=0&sort=display_name'
        result = requests.get(url, auth=(login, password)).content
        jsonresult = json.loads(result)

        count_number = jsonresult['meta']['count']

    except urllib2.URLError, e:
        print
        "Error: cannot connect to the API: %s" % (e)
        print
        "Check your URL & try to login using the same user/pass via the WebUI and check the error!"
        sys.exit(1)
    except Exception, e:
        print
        "FATAL Error - %s" % (e)
        sys.exit(2)



    limit = 100
    offset = 0
    # offset = 2100
    try:
        next_url = jsonresult['links']['next']
    except KeyError:
        next_url = None

    while (next_url is not None):
        url = 'https://' + server + '/api/rhsm-subscriptions/v1/hosts/products/RHEL?limit=100&offset=' + str(offset) + '&sort=display_name'
        offset = offset + 100
        print "[VERBOSE] Connecting to -> %s " % (url)
        result = requests.get(url, auth=(login, password)).content
        jsonresult = json.loads(result)
        systemdata += jsonresult['data']

        try:
            next_url = jsonresult['links']['next']
        except KeyError:
            next_url = None


    stage_lst = []
    for srv_inv in inventory_list:
        count = 0
        for srv_swatch in systemdata:
            if srv_swatch['inventory_id'] == srv_inv[0]:
                count = count + 1
                stage_lst = stage_lst + srv_inv

                inventory_id_swatch = [srv_swatch['inventory_id']]
                stage_lst = stage_lst + inventory_id_swatch

                cores_swatch = [srv_swatch['cores']]
                stage_lst = stage_lst + cores_swatch

                display_name_swatch = [srv_swatch['display_name']]
                stage_lst = stage_lst + display_name_swatch

                hardware_type_swatch = [srv_swatch['hardware_type']]
                stage_lst = stage_lst + hardware_type_swatch
                
                inventory_id_swatch = [srv_swatch['inventory_id']]
                stage_lst = stage_lst + inventory_id_swatch
                
                last_seen_swatch = [srv_swatch['last_seen']]
                stage_lst = stage_lst + last_seen_swatch
                
                measurement_type_swatch = [srv_swatch['measurement_type']]
                stage_lst = stage_lst + measurement_type_swatch
                
                try:
                    number_of_guests_swatch = [srv_swatch['number_of_guests']]
                    stage_lst = stage_lst + number_of_guests_swatch
                except KeyError:
                    number_of_guests_swatch = ["no number_of_guests key"]
                    stage_lst = stage_lst + number_of_guests_swatch
                
                sockets_swatch = [srv_swatch['sockets']]
                stage_lst = stage_lst + sockets_swatch
                
                subscription_manager_id_swatch = [srv_swatch['subscription_manager_id']]
                stage_lst = stage_lst + subscription_manager_id_swatch
                
            
        if count == 1:
            complete_dataset_list.append(stage_lst)
            stage_lst = []
        else:
            stage_lst = srv_inv + ["not in swatch","not in swatch","not in swatch","not in swatch","not in swatch","not in swatch","not in swatch","not in swatch"]
            complete_dataset_list.append(stage_lst)
            stage_lst = []



def csv_export_swatch():
    """
    Function that will generate the final csv file.
    """
    with open('insights_swatch_match.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file)

        for rows in complete_dataset_list:
            csv_writer.writerow(rows)

        print "The file insights_swatch_match.csv was created!"








if __name__ == "__main__":

    default_server = "cloud.redhat.com"
    default_login = "default"
    default_password = ""

    parser = OptionParser()
    # parser.add_option("-l", "--login", dest="login", help="Login user", metavar="LOGIN", default=default_login)
    parser.add_option("-l", "--login", dest="login", help="Login user", metavar="LOGIN")
    parser.add_option("-f", "--filename", dest="filename", help="Login user", metavar="FILENAME")
    parser.add_option("-p", "--password", dest="password", help="Password for specified user. Will prompt if omitted", metavar="PASSWORD", default=default_password)
    parser.add_option("-s", "--server", dest="server", help="FQDN of server - omit https://", metavar="SERVER", default=default_server)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="Verbose output")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Debugging output (debug output enables verbose)")
    (options, args) = parser.parse_args()

    class error_colors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'

    if not (options.login and options.server):
        print "Must specify login, server, and orgid options.  See usage:"
        parser.print_help()
        print "\nExample usage: ./insights-inventory-exporter.py -l admin -s cloud.redhat.com"
        sys.exit(1)
    else:
        login = options.login
        password = options.password
        server = options.server

    if options.filename:
        FILENAME = options.filename
        FILEINPUTMODE = True
    elif not (options.login and options.server):
        print "Must specify login, server, and orgid options.  See usage:"
        parser.print_help()
        print "\nExample usage: ./insights-inventory-exporter.py -l admin -s cloud.redhat.com"
        sys.exit(1)
    else:
        FILEINPUTMODE = False

    login = options.login
    password = options.password
    server = options.server

    if not (FILEINPUTMODE or password):
        password = getpass.getpass("%s's password:" % login)

    # To process all the CH information from cloud.redhat.com
    process_info(login, password, server)

    # Collecting the list of guests running on top of the hypervisors list
    hypervisor_guests()

    # Exporting the data to the csv file
    csv_export()

    # Collecting and processing the info from Inventory and Swatch
    process_info_swatch(login, password, server)

    # Generating the final file
    csv_export_swatch()