import requests
from lxml import etree
import re

JSRU_URL='http://jsru.kb.nl/sru/sru'

def getPPN(fn):
        '''
        Retrieve metadata (currently just publication date) with sru.
        '''
        part=fn.split('.tif')
        part=re.split('[\-_]', part[0])
        str=re.sub(r'([0-9]+)([A-Za-z]+)([0-9]+)',r'\1 \2 \3',part[0])
        map=part[1].lstrip('0')
        omslag=part[2].lstrip('0')
        query1='"' + str + '" and "map ' + map + '" and "omslag ' + omslag + '"'
        query2='"' + str + '" and map not omslag'
        query3='"' + str + '"'
        payload = {}
        payload['operation'] = 'searchRetrieve'
        payload['x-collection'] = 'GGC'
        payload['recordSchema'] = 'dcx'
        payload['query'] = query1

        response = requests.get(JSRU_URL, params=payload, timeout=30)
        assert response.status_code == 200, 'Error retrieving metadata'
        xml = etree.fromstring(response.content)
        path = ".//{http://purl.org/dc/elements/1.1/}identifier[@{http://www.w3.org/2001/XMLSchema-instance}type='dcterms:URI']"
        ppn_element = xml.find(path)
        found_ppn=None
        if ppn_element is not None:
            part=ppn_element.text.split('urn=PPN:')
            found_ppn=part[1]
        else:
            payload['query'] = query2
            response = requests.get(JSRU_URL, params=payload, timeout=30)
            assert response.status_code == 200, 'Error retrieving metadata'
            xml = etree.fromstring(response.content)
            path = ".//{http://purl.org/dc/elements/1.1/}identifier[@{http://www.w3.org/2001/XMLSchema-instance}type='dcterms:URI']"
            ppn_element = xml.find(path)
            if ppn_element is not None:
                part=ppn_element.text.split('urn=PPN:')
                found_ppn=part[1]
            else:
                payload['query'] = query3
                response = requests.get(JSRU_URL, params=payload, timeout=30)
                assert response.status_code == 200, 'Error retrieving metadata'
                xml = etree.fromstring(response.content)
                path = ".//{http://purl.org/dc/terms/}isPartOf[@{http://krait.kb.nl/coop/tel/handbook/telterms.html}recordIdentifier]"
                ppn_element = xml.find(path)
                if ppn_element is not None:
                    ppn=ppn_element.attrib["{http://krait.kb.nl/coop/tel/handbook/telterms.html}recordIdentifier"]
                    part=ppn.split('AC:')
                    found_ppn=part[1]
        return found_ppn
