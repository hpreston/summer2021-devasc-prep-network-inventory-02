# Summer 2021 DevNet Associate Preperation Webinar Series: Software Defined Network Inventory – Adding ACI and SD-WAN

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/hpreston/summer2021-devasc-prep-network-inventory-02)

This repository provides code and examples as part of a [DevNet Associate Certification Preparation Webinar Series](https://learningnetwork.cisco.com/s/article/devnet-associate-prep-program-in-one-place). The recording for this webinar, and others, can be found in the [DevNet Associate Prep Program Training Plan](https://learningnetwork.cisco.com/s/learning-plan-detail-standard?ltui__urlRecordId=a1c3i0000007q9cAAA&ltui__urlRedirect=learning-plan-detail-standard&t=1596603514739).

Slides from the webinar and discussions about the topic can be found in this [forum post from the Learning Network]().

### Software Defined Network Inventory – Adding ACI and SD-WAN

> Your work on an automated network inventory report for your switches and routers was such a big hit that the manager of the SDN team would like you to add the hardware from the ACI and SD-WAN networks to the report. This will be your first chance to explore the REST APIs for these tools!

## Using this repository 
If you'd like to explore the solution to the above use case yourself, here is everything you should need to know.  

### Lab/Sandbox Resources 
This example leverages three DevNet Sandboxes.

* [Cisco NSO Reservable Sandbox from DevNet](https://devnetsandbox.cisco.com/RM/Diagram/Index/43964e62-a13c-4929-bde7-a2f68ad6b27c?diagramType=Topology) - Provides the IOS, IOS XE, IOS XR, NX-OS and ASA devices for the original network inventory script developed in a [previous webinar](https://github.com/hpreston/summer2021-devasc-prep-network-inventory-01) and which this repository builds upon. 
    * You can reserve this sandbox for use with the [nso_sandbox_devices.xlsx](nso_sandbox_devices.xlsx) inventory spreadsheet.  
    * The network topology for the Sandbox can be seen with this [network diagram](NSO-Sandbox-Lab-Network-Topology.jpg).
* [Cisco ACI Always On Sandbox from DevNet](https://devnetsandbox.cisco.com/RM/Diagram/Index/5a229a7c-95d5-4cfd-a651-5ee9bc1b30e2?diagramType=Topology) - Provides an ACI controller network to interact with.
    * No reservation is required for this sandbox, but the address and credentials can be found in the Sandbox details. 
* [Cisco SD-WAN Always On Sandbox from DevNet](https://devnetsandbox.cisco.com/RM/Diagram/Index/fa7f7ef9-e224-4ee7-a3fe-0f25506e9db9?diagramType=Topology) - Provides an SD-WAN controller network to interact with.
    * No reservation is required for this sandbox, but the address and credentials can be found in the Sandbox details. 

### Creating the Python venv 
While other versions of Python will likely work, this use case was tested with Python 3.8.  It leverages [pyATS](https://developer.cisco.com/pyats) for interacting with network devices. 

```
# Create your Virtual Env
python3 -m venv venv
source venv/bin/activate

# Install the entire pyATS set of tools
pip install pyats[full] requests

# Install just the basics for this exercise
pip install pyats pyats.contrib genie requests
```

### Creating the pyATS Testbed File 
The pyATS YAML testbed is included with the GitHub repo, but you can create one from the Excel file with this command. 

```
pyats create testbed file \
--path nso_sandbox_devices.xlsx \
--output nso_sandbox_testbed.yaml
```

Some suggested improvements to the created testbed file include: 

* Move credentials from each device to testbed level
* `ASK{}` for Username as well as passwords

These changes are included in the [`improved_nso_sandbox_testbed.yaml`](improved_nso_sandbox_testbed.yaml) file. 

### Running the `network_inventory.py` script 
The [`network_inventory.py`](network_inventory.py) script in the repo should work and be ready to go.  

> Note: The sandbox credentials for devices are `cisco / cisco` in the testbed are. The credentials for the [ACI](https://devnetsandbox.cisco.com/RM/Diagram/Index/5a229a7c-95d5-4cfd-a651-5ee9bc1b30e2?diagramType=Topology) and [SD-WAN](https://devnetsandbox.cisco.com/RM/Diagram/Index/fa7f7ef9-e224-4ee7-a3fe-0f25506e9db9?diagramType=Topology) controllers are listed in the Sandbox Details. 

```
./network_inventory.py improved_nso_sandbox_testbed.yaml --sdwan-address sandbox-sdwan-1.cisco.com --aci-address sandboxapicdc.cisco.com

# OUTPUT
Loading testbed file improved_nso_sandbox_testbed.yaml
Enter default password for testbed: 

Enter value for testbed.credentials.default.username: cisco
Enter enable password for testbed: 

What is the username for sandboxapicdc.cisco.com? admin
What is the password for sandboxapicdc.cisco.com? (input will be hidden) 

What is the username for sandbox-sdwan-1.cisco.com? devnetuser
What is the password for sandbox-sdwan-1.cisco.com? (input will be hidden) 

Connecting to all devices in testbed improved_nso_sandbox_testbed
Gathering show version from device edge-firewall01
Running command show version on device edge-firewall01
  Error: pyATS lacks a parser for device edge-firewall01 with os asa. Gathering raw output to return.
Gathering show inventory from device edge-firewall01
Running command show inventory on device edge-firewall01
Gathering show version from device dist-rtr01
Running command show version on device dist-rtr01
Gathering show inventory from device dist-rtr01
Running command show inventory on device dist-rtr01
Gathering show version from device dist-rtr02
Running command show version on device dist-rtr02
Gathering show inventory from device dist-rtr02
Running command show inventory on device dist-rtr02
Gathering show version from device dist-sw01
Running command show version on device dist-sw01
Gathering show inventory from device dist-sw01
Running command show inventory on device dist-sw01
Gathering show version from device dist-sw02
Running command show version on device dist-sw02
Gathering show inventory from device dist-sw02
Running command show inventory on device dist-sw02
Gathering show version from device edge-sw01
Running command show version on device edge-sw01
Gathering show inventory from device edge-sw01
Running command show inventory on device edge-sw01
  Error: No valid data found from output from device edge-sw01. Gathering raw output to return.
Gathering show version from device internet-rtr01
Running command show version on device internet-rtr01
Gathering show inventory from device internet-rtr01
Running command show inventory on device internet-rtr01

Inventory details will be pulled from Cisco APIC sandboxapicdc.cisco.com

Inventory details will be pulled from Cisco SD-WAN Controller sandbox-sdwan-1.cisco.com

Disconnecting from device edge-firewall01.
Disconnecting from device dist-rtr01.
Disconnecting from device dist-rtr02.
Disconnecting from device dist-sw01.
Disconnecting from device dist-sw02.
Disconnecting from device edge-sw01.
Disconnecting from device internet-rtr01.
Assembling network inventory data from output.
Writing inventory to file 2021-06-14-13-35-58_improved_nso_sandbox_testbed_network_inventory.csv.
```

And it will create a CSV report that looks like 

```csv
device_name,device_os,software_version,uptime,serial_number 
edge-firewall01,asa,9.12(2),7 days 1 hour,9ACJJ5Q1Q1X 
core-rtr01,iosxr,6.3.1,"1 week, 1 hour, 10 minutes",N/A 
core-rtr02,iosxr,6.3.1,"1 day, 23 hours, 24 minutes",N/A 
dist-rtr01,iosxe,16.11.1b,"1 week, 1 hour, 9 minutes",9Y30J7X5QAC 
dist-rtr02,iosxe,16.11.1b,"1 week, 1 hour, 9 minutes",9741BQ3XSZ5 
dist-sw01,nxos,9.2(3),"7 days, 1 hours, 9 minutes",91FK5ZLK8FF 
dist-sw02,nxos,9.2(3),"7 days, 1 hours, 9 minutes",9CUP5WOOV6M 
edge-sw01,ios,15.2(CML,"4 hours, 52 minutes",N/A 
internet-rtr01,iosxe,16.11.1b,"1 week, 1 hour, 9 minutes",9D6J5QHY2PZ
leaf-1,apic-N9K-C9396PX,simsw-4.1(1k),"00 days, 00 hours, 22 mins",TEP-1-101
apic1,apic-VMware Virtual Platform,Unknown,"00 days, 00 hours, 22 mins",TEP-1-1
spine-1,apic-N9K-C9508,simsw-4.1(1k),"00 days, 00 hours, 22 mins",TEP-1-103
leaf-2,apic-N9K-C9396PX,simsw-4.1(1k),"00 days, 00 hours, 22 mins",TEP-1-102
vmanage,sdwan-vmanage,19.2.2,"0 days, 23 hours, 33 minutes",969E8292C5E64183A2563B7A3605B67D
vsmart,sdwan-vsmart,19.2.2,"363 days, 9 hours, 45 minutes",4E500CAE354B4341B322C5DA4BD7588A
vbond,sdwan-vedge-cloud,19.2.2,"250 days, 56 hours, 35 minutes",7AC124B4AED648EB99B9900DD56A405C
```

## Following the development process 
If you'd like to see how the script was built, you can look at the commit log on the `network_inventory.py` file, or explore the files in the [`development-steps`](development-steps/) folder.  You'll find numbered files showing how the script was build, step by step, that you can run individually, or use as resources to create your own file.  

> Note: the development steps in this example build upon the development done on the original network inventory script from the repo [hpreston/summer2021-devasc-prep-network-inventory-01](https://github.com/hpreston/summer2021-devasc-prep-network-inventory-01).

```
ls -l development-steps 

total 304
-rw-r--r-- 1 hpreston hpreston  7986 Jun 11 20:04 01_network_inventory.py
-rw-r--r-- 1 hpreston hpreston  8526 Jun 11 20:04 02_network_inventory.py
-rw-r--r-- 1 hpreston hpreston  8791 Jun 11 20:04 03_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 10091 Jun 11 20:04 04_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 12125 Jun 11 20:04 05_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 12369 Jun 11 20:04 05a_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 12993 Jun 11 20:04 05b_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 13405 Jun 11 20:04 05c_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 13581 Jun 11 20:04 05d_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 13709 Jun 11 20:04 05e_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 14398 Jun 11 20:04 05f_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 14557 Jun 11 20:04 05g_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 15843 Jun 11 20:04 06_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 16493 Jun 11 20:04 07_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 16778 Jun 11 20:04 08_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 17321 Jun 11 20:04 08a_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 17911 Jun 11 20:04 08b_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 18128 Jun 11 20:04 09_network_inventory.py
-rw-r--r-- 1 hpreston hpreston 18130 Jun 11 20:04 10_network_inventory.py```

> Note: letters after a number indicate an improvement to the main step number, or a multi-stage development step.
