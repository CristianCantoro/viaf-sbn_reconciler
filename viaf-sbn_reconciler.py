#! /usr&bin/env python
# *-* coding: utf-8 *-*

import requests
import time
import pywikibot
import logging
from csv import reader, writer

import wikipedia_template_parser as wtp
from unicode_csv import UnicodeWriter

from item import SbnItem, ViafItem
# globals
INFILESBN = '../6600SBN.csv'
INFILEVIAF = '../VIAF-ICCU.csv'

WIKIPAGESOUTFILE = 'itwiki-pages-with-authority-control.csv'
WIKIPAGESINFILE = 'itwiki-pages-with-authority-control.csv'

OUTWIKIFILE = 'itwiki-viaf-sbn.csv'
INWIKIFILE = 'itwiki-viaf-sbn.csv'

SBNPERMURL = 'http://id.sbn.it/af/IT/ICCU/{sbn_code}'
VIAFPERMURL = 'http://viaf.org/viaf/{viaf_code}'

# create a site object for it.wiki
site = pywikibot.getSite('it', 'wikipedia')
repo = site.data_repository()

# logging
LOGFORMAT_STDOUT = {logging.DEBUG: '%(module)s:%(funcName)s:%(lineno)s - %(levelname)-8s: %(message)s',
                    logging.INFO: '%(levelname)-8s: %(message)s',
                    logging.WARNING: '%(levelname)-8s: %(message)s',
                    logging.ERROR: '%(levelname)-8s: %(message)s',
                    logging.CRITICAL: '%(levelname)-8s: %(message)s'
                    }

# --- root logger
rootlogger = logging.getLogger()
rootlogger.setLevel(logging.DEBUG)

lvl_config_logger = logging.DEBUG

console = logging.StreamHandler()
console.setLevel(lvl_config_logger)

formatter = logging.Formatter(LOGFORMAT_STDOUT[lvl_config_logger])
console.setFormatter(formatter)

rootlogger.addHandler(console)

logger = logging.getLogger('viaf-sbn')
logger.setLevel(logging.DEBUG)


# utility functions
def normalize_string(string):
    return string.lower().replace(' ', '_').encode('utf-8')


if __name__ == '__main__':
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

    viaf2sbn = dict()
    sbn2viaf = dict()
    for line in viaf_reader:
        viaf_code = line[0]
        sbn_code = line[1].strip('IT\\ICCU\\')
        viaf2sbn[viaf_code] = sbn_code
        sbn2viaf[sbn_code] = viaf_code

    infileviaf.close()

    wikipages_infile = open(WIKIPAGESINFILE, 'r+')
    wikipages_with_authority_control = [line.strip() for line in wikipages_infile.readlines()]

    # TODO
    # add a command line argument to switch this.
    write_wikipages = False
    if write_wikipages:
        wikipages_with_authority_control = wtp.pages_with_template(
            'Template:Controllo_di_autorità', lang='it')

        logger.debug('no. of pages in it.wiki with authority control: %d'
                     % len(wikipages_with_authority_control))

        wikipagesoutfile = open(WIKIPAGESOUTFILE, 'w+')
        for page in wikipages_with_authority_control:
            wikipagesoutfile.write('{}\n'.format(page.encode('utf-8')))

    wikipedia = dict()
    sbn2wiki = dict()
    viaf2wiki = dict()

    infilewiki = open(INWIKIFILE, 'r')
    wiki_reader = reader(infilewiki)

    for line in wiki_reader:
        page = None
        viaf_code = None
        sbn_code = None
        try:
            page = line[0]
            viaf_code = line[1]
            sbn_code = line[2]
        except:
            pass

        if page:
            wikipedia[page] = {'viaf': viaf_code,
                               'sbn': sbn_code}
        if viaf_code:
            viaf2wiki[viaf_code] = page

        if sbn_code:
            sbn2wiki[sbn_code] = page

    outwikifile = open(OUTWIKIFILE, 'a+')
    wikiwriter = UnicodeWriter(outwikifile)

    wikipages_to_get = set(wikipages_with_authority_control) - set(wikipedia.keys())

    logger.debug('Wikipages with authority control: {no}'.format(
        no=len(set(wikipages_with_authority_control))))
    logger.debug('no. of keys already collected: {no}'.format(
        no=len(set(wikipedia.keys()))))
    logger.debug('no. of pages in it.wiki with authority control, still to get: {no}'.format(
        no=len(wikipages_to_get)))

    count = 0
    for page in wikipages_to_get:
        count += 1
        logger.debug(count)

        viaf_code = None
        sbn_code = None
        templates = []

        try:
            templates = wtp.data_from_templates(page, lang='it')
        except:
            pass

        ac_template = [t for t in templates
                       if normalize_string(t['name']) == 'controllo_di_autorità']
        ac_data = ac_template[0]['data'] if ac_template else {}

        logger.debug('page: %s, ac_data: %s' % (page, ac_data))
        if ac_data.get('VIAF') is not None:
            logger.debug('VIAF from template')
            viaf_code = ac_data['VIAF']
        if ac_data.get('SBN') is not None:
            logger.debug('SBN from template')
            sbn_code = ac_data['SBN']

        try:
            wikipage = pywikibot.Page(site, page)
        except:
            pass

        item = None
        skip_item = False
        try:
            item = pywikibot.ItemPage.fromPage(wikipage)
            item.get()
            if item.claims:
                if 'p214' in item.claims:  # VIAF identifier
                    viaf_code_wikidata = item.claims['p214'][0].getTarget()
                    logger.debug('page: %s, viaf_code_wikidata: %s' % (page, viaf_code_wikidata))
                    if viaf_code is None:
                        viaf_code = viaf_code_wikidata
                    else:
                        if viaf_code != viaf_code_wikidata:
                            logger.error("VIAF codes in Wikipedia and Wikidata don't match")

                if 'p396' in item.claims:  # SBN identifier
                    sbn_code_wikidata = item.claims['p396'][0].getTarget()
                    logger.debug('page: %s, sbn_code_wikidata: %s' % (page, viaf_code_wikidata))
                    if sbn_code is None:
                        sbn_code = sbn_code_wikidata
                    else:
                        if sbn_code != sbn_code_wikidata:
                            logger.error("SBN codes in Wikipedia and Wikidata don't match")
        except:
            pass

        if page:
            wikipedia[page] = {'viaf': viaf_code,
                               'sbn': sbn_code}

        if viaf_code is not None:
            viaf2wiki[viaf_code] = page

        if sbn_code is not None:
            sbn2wiki[sbn_code] = page

        page = page or ''
        viaf_code = viaf_code or ''
        sbn_code = sbn_code or ''

        wikiwriter.writerow([page, viaf_code, sbn_code])
        time.sleep(0.5)

    outwikifile.close()

    viaf_sbn_codes = set(sbn2viaf.keys())
    sbn_codes = set(sbn.keys())

    viaf_sbn_intersection = viaf_sbn_codes.intersection(sbn_codes)

    print 'no. of VIAF-ICCU SBN records: ', len(viaf2sbn)
    print 'no. of ICCU SBN records with description: ', len(sbn)
    print 'no. of elements in the intersection:', len(viaf_sbn_intersection)

    viaf_code = None
    sbn_code = None
    for sbn_code in viaf_sbn_intersection:
        wiki_page = None
        try:
            viaf_code = sbn2viaf[sbn_code]
        except:
            continue

        wiki_page = sbn2wiki.get(sbn_code) or viaf2wiki.get(viaf_code)

        logger.debug(wiki_page)
        if wiki_page:
            import pdb
            pdb.set_trace()

        print 'SBN: ', sbn_code, ' VIAF: ', viaf_code
        sbnurl = SBNPERMURL.format(sbn_code=sbn_code.replace('\\', '/'))
        viafurl = VIAFPERMURL.format(viaf_code=viaf_code)
        req_sbn = requests.get(sbnurl)
        req_viaf = requests.get(viafurl)

        if req_sbn.ok:
            sbn_item = SbnItem(sbn_code, req_sbn.text, req_sbn.url)

        if req_viaf.ok:
            viaf_item = ViafItem(viaf_code, req_viaf.text, req_viaf.url)

        import pdb
        pdb.set_trace()

        time.sleep(1)
