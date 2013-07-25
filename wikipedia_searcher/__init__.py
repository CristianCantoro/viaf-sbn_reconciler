#! /usr/bin/env python
# *-* coding=utf-8 *-*

import requests

WIKIAPI = 'http://{lang}.wikipedia.org/w/api.php'

FORMAT = 'json'


#'http://it.wikipedia.org/w/api.php?action=query&list=search&srsearch=Igino%20Alunni&srprop=timestamp&srlimit=20'
def wikipedia_opensearch(page, lang='it', limit=50, offset=0):

    page = page.replace(' ', '_')
    baseurl = WIKIAPI.format(lang=lang)

    if not ((format != 'json') or (format != 'xml')):
        raise ValueError("format must be either 'json' or 'xml'")

    res = requests.get(baseurl,
                       params={'action': 'opensearch',
                               'search': page,
                               'limit': limit,
                               'namespace': 0,
                               'format': FORMAT
                               }
                       )
    if not res.ok:
        res.raise_for_status()

    result = res.json()[1]

    return result


#'http://it.wikipedia.org/w/api.php?action=query&list=search&srsearch=Igino%20Alunni&srprop=timestamp&srlimit=20'
def wikipedia_search(page, lang='it', limit=500, offset=0, nres=500):

    page = page.replace(' ', '_')
    baseurl = WIKIAPI.format(lang=lang)
    res = requests.get(baseurl,
                       params={'action': 'query',
                               'list': 'search',
                               'srsearch': page,
                               'srlimit': limit,
                               'sroffset': offset,
                               'format': FORMAT
                               }
                       )
    if not res.ok:
        res.raise_for_status()

    result = [x['title'] for x in res.json()['query']['search']]
    try:
        sroffset = res.json()['query-continue']['search']['sroffset']
    except KeyError:
        sroffset = None

    if sroffset:
        if len(result) < nres:
            result += wikipedia_search(page, lang=lang, offset=sroffset)

    return result[:nres]

if __name__ == '__main__':

    print "Search for 'Duomo' (Opensearch API)"
    res = wikipedia_opensearch('Duomo')
    print res

    # print "Search for 'Duomo'"
    # res = wikipedia_search('Duomo')
    # print res

    print "Search for 'Igino Alunni'"
    res = wikipedia_search('Igino Alunni', nres=10)
    print res
