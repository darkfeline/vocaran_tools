#!/usr/bin/env python2

"""
selenium.py

Script for using selenium to download from nicosound

"""

import os
import os.path
import shutil
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

TMPDIR = "tmp"

def is_mp3(name):
    """Check if string is a valid MP3 name

    >>> is_mp3("hi")
    False
    >>> is_mp3("hi.mp3.old")
    False
    >>> is_mp3("hi.Mp3")
    False
    >>> is_mp3("song.mp3")
    True
    >>> is_mp3("song.MP3")
    True

    """

    return name.endswith(('.mp3', '.MP3'))

def is_part(name):
    """Check if string is name of a part file

    >>> is_mp3("hi")
    False
    >>> is_mp3("song.mp3.part")
    True

    """

    return name.endswith('.part')

def dl(id, name):

    """Download the MP3 and save with song
    
    Returns 0 if all went well, 1 otherwise."""

    if not os.path.isdir(TMPDIR):
        os.mkdir(TMPDIR)

    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", os.path.join(os.getcwd(),
        TMPDIR))
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mp3")
    fp.set_preference("browser.download.manager.showAlertOnComplete", False)

    driver = webdriver.Firefox(firefox_profile=fp)
    driver.implicitly_wait(30)
    base_url = "http://nicosound.anyap.info/sound/{}"
    driver.get(base_url.format(id))

    try:
        x = driver.find_element_by_id(
                "ctl00_ContentPlaceHolder1_SoundInfo1_btnExtract2")
        x.click()
    except NoSuchElementException:
        driver.quit()
        # write a dummy file
        with open(name, 'w') as f:
            f.write('dummy')
            f.close()
        shutil.rmtree(TMPDIR)
        return 1

    driver.get('chrome://mozapps/content/downloads/downloads.xul')

    while 1:
        time.sleep(2)
        song = filter(is_part, os.listdir(TMPDIR))
        if len(song) == 0:
            break

    driver.quit()

    song = filter(is_mp3, os.listdir(TMPDIR))
    if len(song) != 1:
        raise Exception('Something is wrong.  ' + str(len(song)) + ' files in '
                + TMPDIR)
    song = song[0]
    name = name
    shutil.move(os.path.join(TMPDIR, song), name)

    shutil.rmtree(TMPDIR)
    return 0

def main(*args):

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('id')
    parser.add_argument('filename')
    args = parser.parse_args(args)

    try:
        return dl(args.id, args.filename)
    except KeyboardInterrupt as e:
        shutil.rmtree(TMPDIR)

if __name__ == "__main__":
    import sys
    code = main(*sys.argv[1:])
    sys.exit(code)
