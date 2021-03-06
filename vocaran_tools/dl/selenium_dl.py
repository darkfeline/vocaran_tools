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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

TMPDIR = "tmp{}"

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

    tmp = TMPDIR.format('')
    i = 0
    while os.path.exists(tmp):
        i += 1
        tmp = TMPDIR.format(i)
    os.mkdir(tmp)

    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", os.path.join(os.getcwd(), tmp))
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mp3")
    fp.set_preference("browser.download.manager.showAlertOnComplete", False)

    driver = webdriver.Firefox(firefox_profile=fp)
    wait = WebDriverWait(driver, 10)
    base_url = "http://nicosound.anyap.info/sound/{}"
    driver.get(base_url.format(id))
    try:
        wait.until(lambda driver: driver.find_element_by_id(
            'ctl00_ContentPlaceHolder1_SoundInfo1_btnExtract2'))
    except TimeoutException:
        driver.quit()
        shutil.rmtree(tmp)
        return 1

    x = driver.find_element_by_id(
            "ctl00_ContentPlaceHolder1_SoundInfo1_btnExtract2")
    x.click()

    driver.get('chrome://mozapps/content/downloads/downloads.xul')

    while 1:
        time.sleep(2)
        song = filter(is_part, os.listdir(tmp))
        if len(song) == 0:
            break

    driver.quit()

    song = filter(is_mp3, os.listdir(tmp))
    if len(song) != 1:
        raise Exception('Something is wrong.  ' + str(len(song)) + ' files in '
                + tmp)
    song = song[0]
    name = name
    shutil.move(os.path.join(tmp, song), name)

    shutil.rmtree(tmp)
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
