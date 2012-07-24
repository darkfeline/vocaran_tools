#!/usr/bin/env python3

"""
vocaloidism.py

"""

import urllib.request

def get_vocaloidism(outfile, number):
    """Download ranking page source from Vocaloidism.
    
    Get HTML source for the ranking page and save in given file.
    
    """
    conn = urllib.request.urlopen(
        'http://www.vocaloidism.com/weekly-vocaloid-ranking-{}/'.format(number))
    data = conn.read()
    with open(outfile, 'wb') as f:
        f.write(data)
    conn.close()
