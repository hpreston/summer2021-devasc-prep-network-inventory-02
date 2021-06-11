#! /usr/bin/env python
"""
A basic network inventory generation script. 

Goal: 
 - Create a CSV inventory file 
    device name, software version, uptime, serial number

"""

from pyats.topology.loader import load
from genie.libs.parser.utils.common import ParserNotFound
from genie.metaparser.util.exceptions import SchemaEmptyParserError
import re
import csv
from datetime import datetime
import requests 
import urllib3 

# disable InsecureRequestWarning for self-signed certificates 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_command(device, command): 
    """
    Attempt to parse a command on a device with pyATS.
    In case of common errors, return best info possible.
    """

    print(f"Running command {command} on device {device.name}")
    try: 
        output = device.parse(command)
        return {"type": "parsed", "output": output}
    except ParserNotFound: 
        print(f"  Error: pyATS lacks a parser for device {device.name} with os {device.os}. Gathering raw output to return.")
    except SchemaEmptyParserError: 
        print(f"  Error: No valid data found from output from device {device.name}. Gathering raw output to return.")

    # device.execute runs command, gathers raw output, and returns as string
    output = device.execute(command)
    return {"type": "raw", "output": output}

def auth_aci(aci_address, aci_username, aci_password): 
    """
    Retrieve Authentication Token from ACI Controller
    """

    # The API Endpoint for authentication 
    url = f"https://{aci_address}/api/aaaLogin.json"

    # The data payload for authentication 
    payload = {"aaaUser": 
                {
                    "attributes": {
                        "name": aci_username,
                        "pwd": aci_password
                    }
                }
            }

    # Send the request to the controller  
    try: 
        response = requests.post(url, json=payload, verify=False)

        # If the authentiction request succeeded, return the token
        if response.status_code == 200: 
            return response.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
        else: 
            return False
    except Exception as e: 
        print("  Error: Unable to authentication to APIC")
        print(e)
        return False 
    
def lookup_aci_info(aci_address, aci_username, aci_password): 
    """
    Use REST API for ACI to lookup and return inventory details

    In case of an error, return False.
    """

    # Authenticate to API 
    token = auth_aci(aci_address, aci_username, aci_password)
    # For debug print token value 
    # print(f"aci_token: {token}")

    if not token: 
        print(f"  Error: Unable to authenticate to {aci_address}.")
        return False

    # Put token into cookie dict for requests
    cookies = {"APIC-cookie": token}
    
    # List to hold data for each device from controller
    inventory = []
    
    # Send API Request(s) for information 
    # API URLs
    node_list_url = f"https://{aci_address}/api/node/class/fabricNode.json"
    node_firmware_url = "https://{aci_address}/api/node/class/{node_dn}/firmwareRunning.json"
    node_system_url = "https://{aci_address}/api/node/mo/{node_dn}.json?query-target=children&target-subtree-class=topSystem"

    # Lookup Node List from controller
    node_list_rsp = requests.get(node_list_url, cookies=cookies, verify=False)
    # For debug, print response details 
    # print(f"node_list_rsp status_code: {node_list_rsp.status_code}")
    # print(f"node_list_rsp body: {node_list_rsp.text}")

    if node_list_rsp.status_code != 200: 
        print(f"  Error looking up node list from APIC. Status Code was {node_list_rsp.status_code}")
        return False 

    # Loop over nodes
    fabric_nodes = node_list_rsp.json()["imdata"]
    for node in fabric_nodes: 
        # Pull information on node from list 
        node_name = node["fabricNode"]["attributes"]["name"]
        node_model = node["fabricNode"]["attributes"]["model"]
        node_serial = node["fabricNode"]["attributes"]["serial"]

        # Lookup Firmware info with API 
        node_firmware_rsp = requests.get(
            node_firmware_url.format(aci_address=aci_address, node_dn=node["fabricNode"]["attributes"]["dn"]), 
            cookies=cookies, verify=False
            )
        # For debug, print response details 
        # print(f"node_firmware_rsp status_code: {node_firmware_rsp.status_code}")
        # print(f"node_firmware_rsp body: {node_firmware_rsp.text}")

        if node_firmware_rsp.status_code == 200:
            if node_firmware_rsp.json()["totalCount"] == "1": 
                node_software = node_firmware_rsp.json()["imdata"][0]["firmwareRunning"]["attributes"]["version"]
            else: 
                node_software = "Unknown"
        else:
            node_software = "Error"

        # Lookup Uptime info with API
        node_uptime = None

        # Compile and return information
        inventory.append( (node_name, f"apic-{node_model}", node_software, node_uptime, node_serial) )

    return inventory

def lookup_sdwan_info(sdwan_address, sdwan_username, sdwan_password): 
    """
    Use REST API for ACI to lookup and return inventory details

    In case of an error, return False.
    """

    # Authenticate to API 

    # Send API Request(s) for information 

    # Logout API

    # Compile and return information

    return False

def get_device_inventory(device, show_version, show_inventory): 
    """
    Given a testbed device and the output dictionaries, return the 
    required network inventory data for the device. Must consider 
    device OS and address raw/parsed output appropriately.

    return (device_name, device_os, software_version, uptime, serial_number)
    """

    # Common device details from testbed device
    device_name = device.name
    device_os = device.os

    # Build inventory report data structure 
    #   IOS / IOS XE
    #     software version: show version output ["output"]["version"]["version"]
    #     uptime:           show version output ["output"]["version"]["uptime"]
    #     serial:           show inventory output ["main"]["chassis"][MODEL]["sn"]
    #   IOS XR
    #     software version: show version output ["output"]["software_version"]
    #     uptime:           show version output ["output"]["uptime"]
    #     serial:           show inventory output ["output"]["module_name"][MODULE]["sn"]
    #   NXOS 
    #     software version: show version output ["output"]["platform"]["software"]["system_version"]
    #     uptime:           show version output ["output"]["platform"]["kernel_uptime"] : 
    #                                  {'days': 6, 'hours': 20, 'minutes': 48, 'seconds': 59}
    #     serial:           show inventory output ["output"]["name"]["Chassis"]["serial_number"]
    #   ASA
    #     software version: show version RAW output "Cisco Adaptive Security Appliance Software Version 9.12(2)"
    #     uptime:           show version RAW output "up 6 days 20 hours"
    #     serial:           show inventory output ["Chassis"]["sn"]

    if device.os in ["ios", "iosxe"]: 
        software_version = show_version[device.name]["output"]["version"]["version"]
        uptime = show_version[device.name]["output"]["version"]["uptime"]
        # Skip devices without parsed show inventory data 
        if show_inventory[device.name]["output"] != "": 
            chassis_name = show_version[device.name]["output"]["version"]["chassis"]
            serial_number = show_inventory[device.name]["output"]["main"]["chassis"][chassis_name]["sn"]
        else: 
            serial_number = "N/A"
    elif device.os == "nxos": 
        software_version = show_version[device.name]["output"]["platform"]["software"]["system_version"]
        uptime_dict = show_version[device.name]["output"]["platform"]["kernel_uptime"]
        uptime = f'{uptime_dict["days"]} days, {uptime_dict["hours"]} hours, {uptime_dict["minutes"]} minutes'
        serial_number = show_inventory[device.name]["output"]["name"]["Chassis"]["serial_number"]
    elif device.os == "iosxr": 
        software_version = show_version[device.name]["output"]["software_version"]
        uptime = show_version[device.name]["output"]["uptime"]
        # Grab the serial from first module - should be the RP 
        for module in show_inventory[device.name]["output"]["module_name"].values(): 
            serial_number = module["sn"]
            break
    elif device.os == "asa": 
        # RegEx matches for software version and uptime patterns 
        software_version_regex = "Software Version ([^\n ]*)"
        uptime_regex = f"{device.name} up ([\d]* days? [\d]* hours?)"

        software_version = re.search(software_version_regex, show_version[device.name]["output"]).group(1)
        uptime = re.search(uptime_regex, show_version[device.name]["output"]).group(1)
        serial_number = show_inventory[device.name]["output"]["Chassis"]["sn"]
    else: 
        return False

    return (device_name, device_os, software_version, uptime, serial_number)

# Script entry point
if __name__ == "__main__": 
    import argparse
    from getpass import getpass

    # print("Creating a network inventory script.")

    # Plan for adding ACI and SD-WAN to inventory 
    # Steps: 
    #   1. Additional arguments for ACI and SD-WAN Controllers 
    #      - Optional arguments for addresses of each controller 
    #   2. Request credentials for if needed 
    #      - Use Python "input()" function 
    #   3. Make REST API calls to gather inventory details
    #      - After functions that parse commands for CLI devices
    #   4. Add to network inventory
    #      - Maintain same tuple based format from CLI devices
    #        (device_name, device_os, software_version, uptime, serial_number)
    #      - For device os use "controller-model" format

    # Load pyATS testbed into script 
    # Use argparse to determine the testbed file : https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='Generate network inventory report from testbed')
    parser.add_argument('testbed', type=str, help='pyATS Testbed File')
    parser.add_argument('--aci-address', type=str, help='Cisco ACI Controller address for gathering inventory details')
    parser.add_argument('--sdwan-address', type=str, help='Cisco SD-WAN Controller address for gathering inventory details')
    args = parser.parse_args()

    # Create pyATS testbed object
    print(f"Loading testbed file {args.testbed}")
    testbed = load(args.testbed)

    print () 
    
    # Check if ACI and/or SD-WAN addresses provided 
    if args.aci_address: 
        aci_username = input(f"What is the username for {args.aci_address}? ")
        aci_password = getpass(f"What is the password for {args.aci_address}? (input will be hidden) ")

    print()

    if args.sdwan_address: 
        sdwan_username = input(f"What is the username for {args.sdwan_address}? ")
        sdwan_password = getpass(f"What is the password for {args.sdwan_address}? (input will be hidden) ")

    print()

    # Connect to network devices 
    testbed.connect(log_stdout=False)
    print(f"Connecting to all devices in testbed {testbed.name}")


    # Run commands to gather output from devices 
    show_version = {}
    show_inventory = {}

    for device in testbed.devices: 
        print(f"Gathering show version from device {device}")
        show_version[device] = parse_command(testbed.devices[device], "show version")
        # print(f"{device} show version: {show_version[device]}")

        print(f"Gathering show inventory from device {device}")
        show_inventory[device] = parse_command(testbed.devices[device], "show inventory")
        # print(f"{device} show inventory: {show_inventory[device]}")

    print()

    # Gather info on inventory from ACI and SD-WAN if info provided 
    if args.aci_address: 
        print(f"Inventory details will be pulled from Cisco APIC {args.aci_address}")
        aci_info = lookup_aci_info(args.aci_address, aci_username, aci_password)

        # for debug, print results
        print(aci_info)

    print()

    if args.sdwan_address: 
        print(f"Inventory details will be pulled from Cisco SD-WAN Controller {args.sdwan_address}")
        sdwan_info = lookup_sdwan_info(args.sdwan_address, sdwan_username, sdwan_password)

        # for debug, print results
        print(sdwan_info)


    print()
    

    # Disconnect from network devices 
    for device in testbed.devices: 
        print(f"Disconnecting from device {device}.")
        testbed.devices[device].disconnect()

    # Build inventory report data structure 
    print("Assembling network inventory data from output.")
    network_inventory = []
    for device in testbed.devices: 
        network_inventory.append(
            get_device_inventory(testbed.devices[device], show_version, show_inventory)
            )

    # print(f"network_inventory = {network_inventory}")

    # Generate CSV file of data
    now = datetime.now()
    inventory_file = f'{now.strftime("%Y-%m-%d-%H-%M-%S")}_{testbed.name}_network_inventory.csv'
    print(f'Writing inventory to file {inventory_file}.')
    with open(inventory_file, 'w', newline='') as csvfile:
        inv_writer = csv.writer(csvfile, dialect="excel")
        # Write header row
        inv_writer.writerow(("device_name", "device_os", "software_version", "uptime", "serial_number"))
        for device in network_inventory: 
            inv_writer.writerow(device)