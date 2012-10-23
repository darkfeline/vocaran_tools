from lxml import etree

def parse_song_info(xml):
    songs = []
    tree = etree.parse(xml)
    list = tree.getroot()
    for song in list:
        si = SongInfo()
        songs.append(si)
        for i in range(len(song)):
            attr = song[i]
            setattr(si, attr.tag, attr.text)
    return songs

class SongInfo:

    def __init__(self):
        self.name = ''
        self.vocalists = ''
        self.producers = ''
        self.type = ''
        self.albums = ''
        self.tags = ''
