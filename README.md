# NSX-Query-Security-Groups
A small python script to query VMware NSX-v to display all members of a specific security group.

##Prerequisites
Requires the Requests libraby to be installed. Requests can be downloaded a from the following URL
http://docs.python-requests.org/en/latest/

##Usage
```
python nsx-query-services.py -h
```
Output:
```
usage: nsx-query-sg.py [-h] [-u [user]] -n nsxmgr [-sg sgName] [-l]

Queries NSX Manager for all members of the specified security group

optional arguments:
  -h, --help  show this help message and exit
  -u [user]   OPTIONAL - NSX Manager username (default: admin)
  -n nsxmgr   NSX Manager hostname, FQDN or IP address
  -sg sgName  Security Group Name
  -l          List all security groups
```
##Examples
### Example 1
Run the following command to list all security groups
```
python nsx-query-sg.py -n 10.29.4.11 -l
```
Output:
```
#########################################################################################
                                     SECURITY GROUPS                                     
#########################################################################################
ObjectID          Security Group Name            Description                             
----------------  -----------------------------  ----------------------------------------
securitygroup-14  SG-DB                                                                  
securitygroup-10  SG-S.Dev Machines              All Dev Machines                        
securitygroup-12  SG-Web                                                                 
securitygroup-11  SG-S.Prod Machines             All Production workloads on the NSX Cluster
securitygroup-1   Activity Monitoring Data Coll  All Production workloads on the NSX Cluster
securitygroup-13  SG-App                                                                 
```
###Example 2
Run the following command to find all members of a specific security group
```
python nsx-query-sg.py -n 10.29.4.11 -sg "SG-S.Prod Machines"
```
Output:
```
#########################################################################################
                                     STATIC INCLUDES                                     
#########################################################################################
ObjectID          ObjectType                     Name                                    
----------------- ------------------------------ ----------------------------------------
vm-38             VirtualMachine                 web-pro-01                              
ipset-2           IPSet                          NET-10.29.0.0/16                        
securitytag-7     SecurityTag                    AntiVirus.virusFound                    
domain-c28        ClusterComputeResource         Dev                                     
datacenter-21     Datacenter                     SneakU                                  
ipset-3           IPSet                          google-public-dns-a.google.com          
5031acba-3df2-... Vnic                           med-web-01 - Network adapter 1          
dvportgroup-50    DistributedVirtualPortgroup    Production VMs                          


#########################################################################################
                                      IP ADDRESSES                                       
#########################################################################################
Addresses                                                                                
--------------------------------------------------                                                                        
fe80::250:56ff:feb1:72df
10.29.6.101
10.29.0.0/16
8.8.8.8
10.29.5.101
fe80::250:56ff:feb1:a666


#########################################################################################
                                    VIRTUAL MACHINES                                     
#########################################################################################
ObjectID          VM Name                                                                
----------------  -----------------------------                                          
vm-40             med-web-01                                                             
vm-38             web-pro-01                                                             
vm-46             sales-app-01                                                           
vm-45             sales-web-02                                                           
vm-39             Ubuntu Template                                                        
vm-47             sales-db-01                                                            
vm-44             sales-web-01                                                           
vm-41             med-web-02                                                             
vm-43             med-db-01                                                              
vm-42             med-app-01                                                             

```
