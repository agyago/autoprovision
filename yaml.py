#! /usr/bin/python3
import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('-n','--name',type=str,dest='name',action='store',help="Hostname",required=True)
parser.add_argument('-s','--size',choices=['small','medium','large','xlarge'],action='store', dest='size',required=True)
parser.add_argument('-d','--dc',choices=['smfc', 'atlc'], action='store', dest='dc', required=True,help='Datacenter')
parser.add_argument('-os',choices=['centos7','debian10','win16'],action='store',dest='os',required=True,help="OS")
parser.add_argument('-ip',action='store',required=True,dest='ip',help="IP")
parser.add_argument('-dev',default='dev')
parser.add_argument('-u', action='store', dest='username', required=True,help='VSphere Username')
parser.add_argument('-f', action='store', dest='vm_file',help="input file containing")

parsed = parser.parse_args()

if parsed.vm_file == None:
    print(parsed.name,parsed.size,parsed.dc,parsed.os,parsed.ip,parsed.dev)
else:
    with open(parsed.vm_file,'r') as file:
        vm_list = [line.replace(" ",",").strip() for line in file.readlines()]
    print(vm_list)