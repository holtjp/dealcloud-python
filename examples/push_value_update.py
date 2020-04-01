"""
This script pushes a new value to the EBITDA field for the "Project Genome"
entry on the Deal list
"""

import getpass as gp
import sys

import requests
import zeep
from zeep import xsd

import dealcloud as dc


# Create an instance of a client for the DealCloud Data Service and a service
# proxy
try:
    client = dc.create_client(
        email=input('Email: '), password=gp.getpass(),
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


# Find all of the entries on the Deal list and try to find the 'Project Genome'
# entry by name
entries = service.GetListEntries(deal_list.Id)
try:
    deal_entry = list(filter(lambda e: e.Name == 'Project Genome', entries))[0]
except IndexError:
    print('Project Genome could not be found.')
    sys.exit()


# Find all of the fields on all of the lists in a site, get the EBITDA field on
# the Deal list
fields = service.GetFields()
try:
    deal_field = list(filter(
        lambda f: f.EntryListId == deal_list.Id and f.Name == 'EBITDA',
        fields
    ))[0]
except IndexError:
    print('Fields could not be found.')
    sys.exit()


# Create a type factory to access the types provided by the service
factory = client.type_factory('ns0')


# Build the payload for your request and push it
requests = factory.ArrayOfDCPush()
value = xsd.AnyObject(xsd.Decimal(), 1.9)
p = factory.DCPush(EntryId=deal_entry.Id, FieldId=deal_field.Id, Value=value)
requests.DCPush.append(p)
try:
    responses = service.ProcessDCPush(
        entryListId=deal_list.Id, requests=requests
    )
except zeep.exceptions.Fault:
    print('An error occurred with the server.')
    sys.exit()


# Check your responses for any errors and print messages appropriately
for r in responses:
    if r.Error is None:
        print(f'Field {r.FieldId} of Entry {r.EntryId} updated successfully.')
    else:
        print(f'Error occurred for Field {r.FieldId} of Entry {r.EntryId}.')
        print(f'Message: {r.Error.Description}')
