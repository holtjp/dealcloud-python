"""
This script deletes an entry from the Deal list
"""

import getpass as gp
import sys

import requests

import dealcloud as dc


# Create an instance of a client for the DealCloud Data Service and a service
# proxy
try:
    client = dc.create_client(
        email=input('Email: '),
        password=gp.getpass(),
        hostname=input('Hostname: ')
    )
except requests.exceptions.ConnectionError:
    print('Failed to connect to the DealCloud Web Service.')
    sys.exit()
service = dc.bind_service(client)


# Find all of the lists in the site and try to find the Deal list by name
lists = service.GetEntryLists()
try:
    deal_list = list(filter(lambda l: l.Name == 'Deal', lists))[0]
except IndexError:
    print('Deal list could not be found.')
    sys.exit()


# Find all of the entries on the Deal list and try to find the 'Project Beta'
# entry by name
entries = service.GetListEntries(deal_list.Id)
try:
    deal_entry = list(filter(lambda e: e.Name == 'Project Beta', entries))[0]
except IndexError:
    print('Jay Test entry could not be found.')
    sys.exit()


# Find all of the fields on all of the lists in a site, get the ones on the
# Deal list
fields = service.GetFields()
deal_fields = list(filter(
    lambda f: f.EntryListId == deal_list.Id, fields
))


# Create a type factory to access the types provided by the DealCloud service
factory = client.type_factory('ns0')


# Build another payload to push data into the site
push_requests = factory.ArrayOfDCPush()
push = factory.DCPushDelete(EntryId=deal_entry.Id, IsDelete=True)
push_requests.DCPush.append(push)
push_responses = service.ProcessDCPush(
    entryListId=deal_list.Id, requests=push_requests
)

# Iterate over your responses and print them to the console
for r in push_responses:
    if r.Error is None:
        print(f'Entry {r.EntryId} successfully deleted.')
    else:
        print(f'ERROR: {r.Error}')
