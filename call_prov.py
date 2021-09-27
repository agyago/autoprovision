#! /usr/bin/env python3
import argparse
import yaml
import ansible_runner # require too install ansible_runner and ansible module
import getpass
import os
import json
import ast


parser = argparse.ArgumentParser()
parser.add_argument('--name',type=str,dest='name',action='store',help="Hostname",required=True)
parser.add_argument('--size',choices=['small','medium','large','xlarge'],action='store', dest='size',default='small')
parser.add_argument('--storage',action='store',dest='storage',help="harddisk_size",default='100')
parser.add_argument('-d','--dc',choices=['dc1', 'dc2'], action='store', dest='dc', help='Datacenter',default='dc1')
parser.add_argument('-env',choices=['prod', 'dev'], action='store', dest='env', help='state',default='dev')
parser.add_argument('-os',choices=['centos','debian','win16'],action='store',dest='os',help="OS",default='centos7')
parser.add_argument('-ip',action='store',dest='ip',help="IP",default='None')
parser.add_argument('-t', action='store', dest='vcsa', help='VSphere Host')
parser.add_argument('-u', action='store', dest='username', required=True,help='VSphere Username')
parser.add_argument('-f', action='store', dest='vm_file',help="input file containing")


from ipaddress import ip_network, ip_address
parsed = parser.parse_args()

def read_json(file):
    with open(file, 'r') as file:
        data = file.read()
    dict = ast.literal_eval(data)
    return dict

def get_vmnet(ip, vm_net):
    net_def=('na', 'na', 'na')
    for n in vm_net:
        if ip_address(ip) in ip_network(n['netrange']):
            return (n['name'], n['netmask'], n['gateway'])
    return net_def


vm_array=[]
dc = parsed.dc
vm_define = read_json('dc_config')


if parsed.vm_file == None:
    name,size,dc,os,ip,storage,env=(parsed.name,parsed.size,parsed.dc,parsed.os,parsed.ip,parsed.storage,parsed.env)
else:
    with open(parsed.vm_file,'r') as file:
        vm_list = [line.replace(" "," , ").strip() for line in file.readlines()]
    for virtual in vm_list:
        name,size,dc,os,ip,storage,env = virtual.split(",")
vm_net=vm_define['dc'][dc]['network']

netname, netmask, gway = get_vmnet(ip,vm_net)
cluster = vm_define['dc'][dc]['env'][env]['cluster']
dstore = vm_define['dc'][dc]['env'][env]['datastore']

temp_dict={
    'name'   : name,
    'cpu'    : vm_define['dc'][size]['cpu'],
    'memory' : vm_define['dc'][size]['memory'],
    'disk'   : storage,
    'template' : vm_define['dc'][dc]['templates'][os],
    'DC'  : vm_define['dc'][dc]['name'],
    'os'  : os,
    'ip'  : ip,
    'netmask': netmask,
    'gateway': gway,
    'vm_net': netname,
    'cluster': cluster,
    'data_store': dstore,
}

vm_array.append(temp_dict)
vm_call= { 'vms': vm_array}


with open(r'input.yml', 'w') as fh:
    yaml.dump(vm_call, fh)

vc_hostname = parsed.vcsa
vc_username = parsed.username
try:
    vc_pwd = getpass.getpass(prompt="VCenter Password: ")
    guest_root_pwd = getpass.getpass(prompt="Guest Root Password: ")
except Exception as e:
    print(e)
    
ansible_runner.run_command(
    executable_cmd='ansible-playbook',
    cmdline_args=["vm_create.yml",
        "-e", "vc_hostname=" + vc_hostname, 
        "-e", "vc_username=" + vc_username, 
        "-e", "vc_pwd='" + vc_pwd + "'",
        "-e", "guest_root_pwd='" + guest_root_pwd + "'", 
        ])
