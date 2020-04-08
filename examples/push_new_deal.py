"""
This script creates a new entry on the Deal list for "Project Alpha" including
basic deal data and a PDF document with the following data:

    Deal Name:          Project Beta
    Company:            Beta Incorporated
    Status:             Active
    Stage:              1 - New Deal
    EBITDA:             12.5
    New Deal Date:      4/1/2020
    Deal Team:          James Holt
    Attachment:         Teaser.pdf
"""

import datetime as dt
import getpass as gp
import sys

import requests
import zeep
from zeep import xsd

import dealcloud as dc


# Assuming that your data is represented as a dictionary
new_entry = {
    'Deal Name': 'Project Beta',
    'Company': 'Beta Incorporated',
    'Status': 'Active',
    'Stage': '1 - New Deal',
    'EBITDA': 12.5,
    'New Deal Date': '4/1/2020',
    'Deal Team': 'James Holt',
    'attachment': 'Teaser.pdf'
}

# Create new entries by providing a negative Id
new_attachment_id = -1
new_deal_id = -2

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


# Find all of the lists in the site and try to find the Deal and Attachment
# lists
lists = service.GetEntryLists()
try:
    deal_list = list(filter(lambda l: l.Name == 'Deal', lists))[0]
    attachment_list = list(filter(
        lambda l: l.EntryListType == 'Attachment', lists
    ))[0]
except IndexError:
    print('Required lists could not be found.')
    sys.exit()


# Find all of the fields on all of the lists in a site, get the ones you want
# to push new deal data into and all of the required fields
fields = service.GetFields()
deal_fields = dict()
attachment_fields = dict()
for f in fields:
    if f.EntryListId == deal_list.Id \
            and (f.IsRequired or f.Name in new_entry.keys()):
        deal_fields[f.Name] = f
    elif f.EntryListId == attachment_list.Id and f.IsRequired:
        attachment_fields[f.Name] = f
    else:
        continue


# Create a type factory to access the types provided by the service
factory = client.type_factory('ns0')


# Create an array for your DCPushes
push_requests = factory.ArrayOfDCPush()


# Create DCPushes for all of the Attachment fields
filename = new_entry['attachment']
filename_str = xsd.AnyObject(xsd.String(), filename)
push_filename = factory.DCPush(
    EntryId=new_attachment_id, FieldId=attachment_fields['Title'].Id,
    Value=filename_str
)

extension = xsd.AnyObject(xsd.String(), filename.split('.')[-1])
push_extension = factory.DCPush(
    EntryId=new_attachment_id, FieldId=attachment_fields['File Type'].Id,
    Value=extension
)

with open(filename, 'rb') as f:
    content = xsd.AnyObject(xsd.Base64Binary(), f.read())
content_type = xsd.AnyObject(xsd.String(), 'application/pdf')
push_document = factory.DCPushBinary(
    EntryId=new_attachment_id, FieldId=attachment_fields['Document'].Id,
    Value=content, ContentType=content_type, FormatType=extension
)

content_len = xsd.AnyObject(xsd.Decimal(), float(len(content.value)))
push_length = factory.DCPush(
    EntryId=new_attachment_id, FieldId=attachment_fields['Size'].Id,
    Value=content_len
)

push_requests.DCPush += [
    push_filename, push_extension, push_length, push_document
]


# Create the Attachment entry in the site
try:
    push_responses = service.ProcessDCPush(attachment_list.Id, push_requests)
except zeep.exceptions.Fault:
    print('An error occured with the server.')
    sys.exit()


# Check your responses for any errors and print messages appropriately
for r in push_responses:
    if r.Error is None:
        print(f'Field {r.FieldId} of Entry {r.EntryId} updated successfully.')
    else:
        print(f'Error occurred for Field {r.FieldId} of Entry {r.EntryId}.')
        print(f'Message: {r.Error.Description}')
        sys.exit()


# Reset your Array of DCPushes
push_requests.DCPush = list()


# Create DCPushes for all of the data in your new Deal entry
for k, v in deal_fields.items():
    try:
        f = deal_fields[k]
    except KeyError:
        print(f'A value for Field {k} was not found in your data')
        sys.exit()
    p = factory.DCPush(EntryId=new_deal_id, FieldId=f.Id)
    if f.FieldType == 'Text':
        new_value = xsd.AnyObject(xsd.String(), new_entry[k])
    elif v.FieldType in 'Number':
        new_value = xsd.AnyObject(xsd.Decimal(), new_entry[k])
    elif v.FieldType == 'Date':
        new_value = xsd.AnyObject(
            xsd.DateTime(), dt.datetime.strptime(new_entry[k], '%m/%d/%Y')
        )
    elif v.FieldType == 'Boolean':
        if new_entry[k].lower() == 'yes':
            new_value = xsd.AnyObject(xsd.Boolean(), True)
        elif new_entry[k].lower() == 'no':
            new_value = xsd.AnyObject(xsd.Boolean(), False)
        else:
            new_value = None
    elif v.FieldType == 'Choice':
        choices = v.ChoiceValues.ChoiceFieldValue
        targets = new_entry[k].split(';')
        if v.IsMultiSelect:
            choice_ids = list()
            for t in targets:
                try:
                    choice = list(filter(
                        lambda c: c.Name == t, choices
                    ))[0]
                except IndexError:
                    print(f'Choice {t} could not be resolved.')
                    sys.exit()
                choice_ids.append(choice.Id)
            new_value = factory.ListOfInts(choice_ids)
        else:
            if len(targets) > 1:
                print(f'Field {k} is not a Multi-Select field.')
                sys.exit()
            else:
                try:
                    choice = list(filter(
                        lambda c: c.Name == targets[0], choices))[0]
                except IndexError:
                    print(f'{targets[0]} is not a valid Choice Value.')
                    sys.exit()
                new_value = xsd.AnyObject(xsd.Int(), choice.Id)
    elif v.FieldType == 'Reference':
        entries = list()
        for Id in v.EntryLists.int:
            entries += service.GetListEntries(Id)
        targets = new_entry[k].split(';')
        if v.IsMultiSelect:
            entry_ids = list()
            for t in targets:
                try:
                    target_entry = list(filter(
                        lambda e: e.Name == t, entries))[0]
                except IndexError:
                    print(f'Entry {t} could not be found.')
                    sys.exit()
                entry_ids.append(target_entry.Id)
            new_value = factory.ListOfInts(entry_ids)
        else:
            if len(targets) > 1:
                print(f'Field {k} is not a Multi-Select field.')
                sys.exit()
            else:
                try:
                    target_entry = list(filter(
                        lambda e: e.Name == targets[0], entries))[0]
                except IndexError:
                    print(f'Entry {targets[0]} could not be found.')
                    sys.exit()
                new_value = xsd.AnyObject(xsd.Int(), target_entry.Id)
    elif v.FieldType == 'User':
        users = service.GetUsers()
        targets = new_entry[k].split(';')
        if v.IsMultiSelect:
            user_ids = list()
            for t in targets:
                try:
                    user = list(filter(lambda u: u.Name == t, users))[0]
                except IndexError:
                    print(f'User {t} could not be found.')
                    sys.exit()
                user_ids.append(user.Id)
            new_value = factory.ListOfInts(user_ids)
        else:
            if len(targets) > 1:
                print(f'Field {k} is not a Multi-Select field.')
                sys.exit()
            else:
                try:
                    target_entry = list(filter(
                        lambda u: u.Name == targets[0], users))[0]
                except IndexError:
                    print(f'User {targets[0]} could not be found.')
                    sys.exit()
                new_value = xsd.AnyObject(xsd.Int(), target_entry.Id)
    else:
        new_value = None
    p.Value = new_value
    push_requests.DCPush.append(p)


# Push the Deal entry into the site
try:
    push_responses = service.ProcessDCPush(
        entryListId=deal_list.Id, requests=push_requests
    )
except zeep.exceptions.Fault:
    print('An error occurred with the server.')
    sys.exit()


# Check your responses for any errors and print messages appropriately
for r in push_responses:
    if r.Error is None:
        print(f'Field {r.FieldId} of Entry {r.EntryId} updated successfully.')
    else:
        print(f'Error occurred for Field {r.FieldId} of Entry {r.EntryId}.')
        print(f'Message: {r.Error.Description}')
