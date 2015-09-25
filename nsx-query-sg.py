#
# Script to show VMware NSX-v security group members
# Written by Dale Coghlan
# Date: 6 May 2015
# https://github.com/dcoghlan/
# Version: 1.0.2

# ------------------------------------------------------------------------------------------------------------------
# Set some variables. No need to change anything else after this section

# Set the managed object reference
_scope = 'globalroot-0'

# Uncomment the following line to hardcode the NSX Manager.
#_nsxmgr = '10.29.4.11'

# Uncomment the following line to hardcode the password. This will remove the password prompt.
#_password = 'default'

# Show IPv6 addressing in the output [0=No, 1=Yes].
_showIPv6 = '1'
# ------------------------------------------------------------------------------------------------------------------

import requests
import argparse
import getpass
import logging
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString
import socket	# required for checking of IP Addresses

try:
	# Only needed to disable anoying warnings self signed certificate warnings from NSX Manager.
	import urllib3
	requests.packages.urllib3.disable_warnings()
except ImportError:
	# If you don't have urllib3 we can just hide the warnings
	logging.captureWarnings(True)

parser = argparse.ArgumentParser(description='Queries NSX Manager for all members of the specified security group')
parser.add_argument('-u', help='OPTIONAL - NSX Manager username (default: %(default)s)', metavar='user', dest='_user', nargs='?', const='admin')
parser.set_defaults(_user="admin")
parser.add_argument('-n', help='NSX Manager hostname, FQDN or IP address', metavar='nsxmgr', dest='_nsxmgr', type=str, required=True)

# Mutually exclusve argument group
group1 = parser.add_mutually_exclusive_group()
group1.add_argument('-sg', help='Security Group Name', metavar='sgName', dest='_sgName')

# Mutually exclusve argument group
group2 = parser.add_mutually_exclusive_group()
group2.add_argument('-l', help='List all security groups', dest='_listsg', action='store_true')

args = parser.parse_args()

# Check to see if the password has been hardcoded. If it hasn't prompt for the password
try:
	_password
except NameError:
	_password = getpass.getpass(prompt='NSX Manager password:')

# Check to see if the NSX Manager has been hardcoded. If it hasn't take it from the command line arguments
try:
	_nsxmgr
except NameError:
	_nsxmgr = args._nsxmgr

# Reads command line flags and saves them to variables
_user = args._user
_sgName = args._sgName
_listsg = args._listsg

# Set the application content-type header value
_myheaders = {'Content-Type': 'application/xml'}

# Set output formatting
_outputHeaderRow = "{0:17} {1:30} {2:40}"
_outputDataRow = "{0:17} {1:30.29} {2:40}"
_outputSectionRow = "{0:89}"
_outputSectionTitle = "{0:^89}"

def f_smart_truncate(content, length, suffix='...'):
	if len(content) < length:
		return content
	else:
		return content[:length-3] + suffix

def f_get_sg_list():
	print('Retrieving Security Groups via API')

	# NSX API URL to get all services configured in the specified scope
	requests_url = 'https://%s/api/2.0/services/securitygroup/scope/%s' % (_nsxmgr, _scope)

	# Submits the request to the NSX Manager
	success = requests.get((requests_url), headers=_myheaders, auth=(_user, _password), verify=False)

	print('Retrieved all security group')

	# Loads XML response into memory
	doc = parseString(success.text.encode('ascii', 'ignore'))


	# Loads xml document into memory using the application element
	securitygrouplist = doc.getElementsByTagName('securitygroup')

	print('')
	print(_outputSectionRow.format("#"*89))
	print(_outputSectionTitle.format('SECURITY GROUPS'))
	print(_outputSectionRow.format("#"*89))
	print(_outputHeaderRow.format('ObjectID', 'Security Group Name', 'Description'))
	print(_outputHeaderRow.format('-'*16, '-'*29, '-'*40))

	# Iterates through each application element
	for sg in securitygrouplist:
		# clears the list
		data = [];
		# Gets the objectId of the application
		sgObjectId = sg.getElementsByTagName('objectId')[0]
		#sgObjectIdData = sgObjectId[:15] + (sgObjectId[15:] and '..')
		#print(sgObjectIdData)
		# Sets the list to start with the objectID
		data = [(sgObjectId.firstChild.data)]
		# Get the name of the application
		sgName = sg.getElementsByTagName('name')[0]
		# Appends the name name to the list
		data.append(sgName.firstChild.data);
		# Load the description element
		sgDescription = sg.getElementsByTagName('description')
		# Check to see if the description element exists
		if sgDescription:
			# Checks to see if the element has a child
			if sgDescription[0].firstChild:
				# If it contains a child element then append the data to the list
				data.append(sgDescription[0].firstChild.data);
				sgDescriptionData = sgDescription[0].firstChild.data
			else:
				# So if there is no child element, append a blank string to the list
				sgDescriptionData = ''
		else:
			data.append('')
			sgDescriptionData = ''

		print(_outputDataRow.format(sgObjectId.firstChild.data,	sgName.firstChild.data,	sgDescriptionData))


def f_get_sgid(group):
	_get_sec_group_url = 'https://%s/api/2.0/services/securitygroup/scope/%s' % (_nsxmgr, _scope)
	_get_sec_group_reponse = requests.get((_get_sec_group_url), headers=_myheaders, auth=(_user, _password), verify=False)
	_get_sec_group_data = _get_sec_group_reponse.content
	_get_sec_group_root = ET.fromstring(_get_sec_group_data)

	for sgid in _get_sec_group_root.findall('securitygroup'):
		if sgid.find('name').text == group:
			return sgid.find('objectId').text

def f_get_sg_mem_vms(id):
	_get_sec_group_member_vms_url = 'https://%s/api/2.0/services/securitygroup/%s/translation/virtualmachines' % (_nsxmgr, id)
	_get_sec_group_member_vms_reponse = requests.get((_get_sec_group_member_vms_url), headers=_myheaders, auth=(_user, _password), verify=False)
	_get_sec_group_member_vms_data = _get_sec_group_member_vms_reponse.content

	print('')
	print(_outputSectionRow.format("#"*89))
	print(_outputSectionTitle.format('VIRTUAL MACHINES'))
	print(_outputSectionRow.format("#"*89))
	print(_outputHeaderRow.format('ObjectID', 'VM Name', ''))
	print(_outputHeaderRow.format('-'*16, '-'*29, ''*40))

	_get_sec_group_member_vms_dom = parseString(_get_sec_group_member_vms_reponse.text)
	_get_sec_group_member_vms_list = _get_sec_group_member_vms_dom.getElementsByTagName('vmnode')

	# Iterates through each application element
	for vmnodes in _get_sec_group_member_vms_list:
		# Gets the objectId of the member
		vmObjectId = vmnodes.getElementsByTagName('vmId')[0]
		vmName = vmnodes.getElementsByTagName('vmName')[0]
		print(_outputDataRow.format(vmObjectId.firstChild.data,	vmName.firstChild.data,	''))
	print('')

def f_get_sg_mem_ipSets(id):
	_get_sec_group_member_ipSets_url = 'https://%s/api/2.0/services/securitygroup/%s/translation/ipaddresses' % (_nsxmgr, id)
	_get_sec_group_member_ipSets_reponse = requests.get((_get_sec_group_member_ipSets_url), headers=_myheaders, auth=(_user, _password), verify=False)
	_get_sec_group_member_ipSets_data = _get_sec_group_member_ipSets_reponse.content

	print('')
	print(_outputSectionRow.format("#"*89))
	print(_outputSectionTitle.format('IP ADDRESSES'))
	print(_outputSectionRow.format("#"*89))
	print(_outputHeaderRow.format("Addresses", "", ""))
	print(_outputHeaderRow.format("-"*50, "", ""))

	_get_sec_group_member_ipSets_dom = parseString(_get_sec_group_member_ipSets_reponse.text)
	_get_sec_group_member_ipSets_list = _get_sec_group_member_ipSets_dom.getElementsByTagName('ipNode')

	# Iterates through each application element
	for elements in _get_sec_group_member_ipSets_list:
		# looks for the string element.
		string = elements.getElementsByTagName('string')

		# Checks to see if the element exists
		if string:
			# Sometimes there are multiple addresses/strings for an ipNode
			for ipAddress in string:
				if _showIPv6 == '0':
					try:
						socket.inet_pton(socket.AF_INET6, ipAddress.firstChild.data)
					except socket.error:
						print(ipAddress.firstChild.data)
				else:
					print(ipAddress.firstChild.data)
	print('')

def f_get_sg_mem_static_include(id):
	_get_sec_group_member_static_include_url = 'https://%s/api/2.0/services/securitygroup/%s' % (_nsxmgr, id)
	_get_sec_group_member_static_include_reponse = requests.get((_get_sec_group_member_static_include_url), headers=_myheaders, auth=(_user, _password), verify=False)
	_get_sec_group_member_static_include_data = _get_sec_group_member_static_include_reponse.content

	print('')
	print(_outputSectionRow.format("#"*89))
	print(_outputSectionTitle.format('STATIC INCLUDES'))
	print(_outputSectionRow.format("#"*89))
	print(_outputHeaderRow.format("ObjectID", "ObjectType", "Name"))
	print(_outputHeaderRow.format("-"*17, "-"*30, "-"*40))

	_get_sec_group_member_static_include_dom = parseString(_get_sec_group_member_static_include_reponse.text)
	_sec_group_member_static_include_list = _get_sec_group_member_static_include_dom.getElementsByTagName('member')

	# Iterates through each application element
	for member in _sec_group_member_static_include_list:
		# Get the objectId of the member
		memberObjectId = member.getElementsByTagName('objectId')[0]
		# Get the name of the application
		memberObjectType = member.getElementsByTagName('objectTypeName')[0]
		# Get the name of the application
		memberName = member.getElementsByTagName('name')[0]
		print(_outputDataRow.format(f_smart_truncate(memberObjectId.firstChild.data,17), memberObjectType.firstChild.data, memberName.firstChild.data))
	print('')

def main():
	if _listsg:
		f_get_sg_list()
	else:
		_sgId = f_get_sgid(_sgName)
		f_get_sg_mem_static_include(_sgId)
		f_get_sg_mem_ipSets(_sgId)
		f_get_sg_mem_vms(_sgId)

if __name__ == "__main__":
    # execute only if run as a script
    main()

exit()
