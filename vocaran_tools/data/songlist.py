#!/usr/bin/env python3

"""
songlist.py

This module holds class definitions for SongList classes and related classes.

SongList file format
--------------------

::

    file ::= header song_entry* stop
    header ::= week_number [is_done]

    week_number ::= '% ' ('0' ... '9')+ ' \\n'
    is_done ::= '% done \\n'
    entry_start ::= '% start_entry \\n'
    stop ::= '% end \\n'

    song_entry ::= entry_start id name artist album comment apic
    nndid ::= ('s' | 'n') ('m' | 'o') ('0' ... '9')+ '\\n'
    rank ::= (['h'] ('0' .. '9')+ | 'pkp' | 'ed') '\\n'
    id ::= (nndid | rank) '\\n'
    name ::= <any string that doesn't contain '\\n'>
    artist ::= <any string that doesn't contain '\\n'>
    album ::= <any string that doesn't contain '\\n'>
    comment ::= <any string that doesn't contain '\\n'>
    apic ::= ('none' | 'smile' | 'def' | <arbitrary set of strings of integers,
             e.g. '1', '2', '3' ...>) '\\n'

"""

import re
import os

from vocaran_tools.errors import FileFormatError

class SongEntry:

    _nnid = re.compile(r'^[sn][mo][0-9]+$', re.I)
    _save = ('id', 'name', 'artist', 'album', 'comment', 'apic')

    def __init__(self, id='sm1', name='', artist='', album='', comment='',
            apic='none'):
        self.values = {}
        self.id = id
        self.name = name
        self.artist = artist
        self.album = album
        self.comment = comment
        self.apic = apic

    def write_to(self, fpipe):
        for key in self._save:
            fpipe.write(getattr(self, key) + '\n')

    @classmethod
    def read_from(cls, fpipe):
        x = cls()
        for key in cls._save:
            setattr(x, key, fpipe.readline()[:-1])
        return x

    def __iter__(self):
        return iter([getattr(self, x) for x in self._save])

    @property
    def id(self):
        return self.values['id']

    @id.setter
    def id(self, value):
        if not self.__class__._nnid.match(value):
            raise TypeError('"value" must be a valid NNID string.')
        self.values['id'] = value

    @property
    def name(self):
        return self.values['name']

    @name.setter
    def name(self, value):
        self.values['name'] = value

    @property
    def artist(self):
        return self.values['artist']

    @artist.setter
    def artist(self, value):
        self.values['artist'] = value

    @property
    def album(self):
        return self.values['album']

    @album.setter
    def album(self, value):
        self.values['album'] = value

    @property
    def comment(self):
        return self.values['comment']

    @comment.setter
    def comment(self, value):
        self.values['comment'] = value

    @property
    def apic(self):
        return self.values['apic']

    @apic.setter
    def apic(self, value):
        self.values['apic'] = value


class RankedSongEntry(SongEntry):

    _rank = re.compile(r'^h?[0-9]+|ed|pkp$', re.I)

    @property
    def id(self):
        return super().id

    @id.setter
    def id(self, value):
        if self._rank.match(value):
            self.values['id'] = value
        else:
            try:
                super(RankedSongEntry, self.__class__).id.fset(self, value)
            except TypeError:
                raise TypeError('"value" must be a valid NNID string or rank.')


class SongList:

    entry_type = SongEntry
    _special_str = '% {} \n'
    _special_re = re.compile(r'^% (\w+)')

    def __init__(self, file='', week='0'):
        self.week = week
        self.entries = []
        self.file = file
        self.done = False

    @property
    def week(self):
        return self._week

    @week.setter
    def week(self, value):
        self._week = int(value)

    def save(self):
        with open(self.file + '~', 'w') as f:
            f.write(self._special_str.format(str(self.week)))
            if self.done:
                f.write(self._special_str.format('done'))
            for entry in self.entries:
                f.write(self._special_str.format('start_entry'))
                entry.write_to(f)
            f.write(self._special_str.format('end'))
        os.rename(self.file + '~', self.file)

    @classmethod
    def load(cls, file):
        slist = cls(file)
        with open(file, 'r') as f:
            s = f.readline().rstrip()
            m = cls._special_re.match(s)
            slist.week = m.group(1)
            while True:
                s = f.readline().rstrip()
                m = cls._special_re.match(s)
                if m.group(1) == 'end':
                    break
                elif m.group(1) == 'start_entry':
                    slist.add(cls.entry_type.read_from(f))
                elif m.group(1) == 'done':
                    slist.done = True
                else:
                    raise FileFormatError
        return slist

    def add(self, *args, **kwargs):
        entry = self.__class__.entry_type
        if len(args) >= 1 and isinstance(args[0], entry):
            self.entries.append(args[0])
        else:
            self.entries.append(entry(*args, **kwargs))

    def __getitem__(self, key):
        return self.entries[key]

    def __setitem__(self, key, value):
        entry = self.__class__.entry_type
        if not isinstance(value, entry):
            raise TypeError('"value" must be an instance of {}.'.format(
                                                                 str(entry)))
        self.entries[key] = value

    def __delitem__(self, key):
        del self.entries[key]

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)


class RankedSongList(SongList):

    entry_type = RankedSongEntry
