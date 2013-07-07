#! /usr&bin/env python
# *-* coding: utf-8 *-*

from csv import reader

INFILESBN = '../6600SBN.csv'
INFILEVIAF = '../VIAF-ICCU.csv'

infilesbn = open(INFILESBN, 'r')
sbn_reader = reader(infilesbn)

sbn = dict()
for line in sbn_reader:
    code = line[0]
    description = line[1]
    sbn[code] = description

infilesbn.close()

infileviaf = open(INFILEVIAF, 'r')
viaf_reader = reader(infileviaf)

viaf = dict()
for line in viaf_reader:
    viaf_code = line[0]
    sbn_code = line[1].strip('IT\\ICCU\\')
    viaf[viaf_code] = sbn_code
infileviaf.close()

viaf_sbn_codes = set(viaf.values())
sbn_codes = set(sbn.keys())

print 'no. of VIAF-ICCU SBN records: ', len(viaf)
print 'no. of ICCU SBN records with description: ', len(sbn)
print 'no. of elements in the intersection:', len(viaf_sbn_codes.intersection(sbn_codes))
