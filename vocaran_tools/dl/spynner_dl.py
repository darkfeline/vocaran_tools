#!/usr/bin/env python2

import spynner
import pyquery

def dl(id, file):
    browser = spynner.Browser()
    browser.set_html_parser(pyquery.PyQuery)
    browser.load("http://nicosound.anyap.info/sound/{}".format(id))
    try:
        browser.click("[id=ctl00_ContentPlaceHolder1_SoundInfo1_btnExtract2]")
    except spynner.SpynnerJavascriptError:
        return 1
    browser.wait_load()
    data = browser.download(
            "http://ns5.anyap.info:8080/sound/{}.mp3".format(id))
    with open(file, 'wb') as f:
        f.write(data)
    browser.close()
    return 0

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('id')
    parser.add_argument('filename')
    args = parser.parse_args(args)

    return dl(args.id, args.filename)

if __name__ == "__main__":
    import sys
    code = main(*sys.argv[1:])
    sys.exit(code)
