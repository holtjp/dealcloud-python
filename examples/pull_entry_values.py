"""
This script pulls the values of the fields for the "Project Genome" entry on
the Deal list
"""

import getpass as gp
import sys

import requests

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


# Find all of the fields on all of the lists in a site, get the ones on the
# Deal list
fields = service.GetFields()
deal_fields = list(filter(lambda f: f.EntryListId == deal_list.Id, fields))


# Create a type factory to access the types provided by the service
factory = client.type_factory('ns0')


# Build the payload for your request with the types provided by the factory
# and send it
requests = factory.ArrayOfDCPull()
for f in deal_fields:
    p = factory.DCPull(EntryId=deal_entry.Id, FieldId=f.Id)
    requests.DCPull.append(p)
response = service.ProcessDCPull(
    requests=requests, resolveReferenceUrls=True, fillExtendedData=True
)

# Iterate over your responses and print them to the console
for r in response:
    try:
        field = list(filter(lambda f: f.Id == r.FieldId, deal_fields))[0]
    except IndexError:
        print(f'Field {r.FieldId} cound not be named.')
        continue
    print(f'{field.Name}: {r.Value}')
