#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""subtitle convertor:
converts sub/srt files to lrc files.

Usage: python subtitleconv.py [options] [source]

Options:
  -g ..., --grammar=...   use specified grammar file or URL
  -h, --help              show this help

Examples:
  subtitleconv temp.sub[srt]
"""
import re
import os
import sys


class subtitleconv(object):
    def __init__(self, filename):
        """        """
        self.data = {}
        self.filename = filename
        self.srclist = self.__fileloader()
        self.cleansrc = self.postread(self.srclist)
        self.outlist = []
        self.__parser()
        self.__output()

    def __fileloader(self):
        """load source file."""
        try:
            fread = open(self.filename, "rU")
            print self.filename
        except IOError:
            print "file doesn't exist."
            sys.exit(2)
        srclist = fread.readlines()
        self.rnlines = fread.newlines
        fread.close()
        return srclist

    def postread(self, ablist):
        """remove empty lines, mergy concessive white spaces."""
        clnlist  = [line.strip() for line in ablist if line.strip()]
        srcstr = "\n".join(clnlist).expandtabs(4)
        tempattern = re.compile(r" +")
        clnlist = tempattern.sub(r" ", srcstr).split("\n")
        return clnlist

    def __output(self):
        """output .lrc file
        """
        outfile = os.path.splitext(self.filename)[0] + ".lrc"
        try:
            wtfile = open(outfile, "w")
        except IOError:
            print "can't creat a file to write."
            sys.exit(2)
        wtfile.write(self.rnlines.join(self.outlist))
        wtfile.close()
        print "%s  \nDone."  % outfile

    def __parser(self):
        """wraper for sub, srt"""
        subsample = "\n".join(self.cleansrc[:6])
        subtype = [(r"(^|\n)\{\d+\}\{\d+\}", self.__SUBparser),
                   (r"\d{,3} --> \d{2}:\d{2}", self.__SRTparser)]
        for (pattern, subfunc) in subtype:
            if re.search(pattern, subsample):
                subfunc()
                return
        sys.exit("file format is not supported.".title())

    def __SRTparser(self):
        """wraper for *.srt"""
        midlist = []
        sublist = []
        contactline = ""
        timepattern = re.compile(r"^(.+\d{,3}) --> (\d{2}:\d{2}:\d{2}.\d{3})")
        for line in self.cleansrc:
            if not timepattern.search(line):
                sublist.append(line)
                subresv = sublist
                continue
            contactline += "".join(sublist[:-1])
            sublist = []
            midlist.append(contactline)
            contactline = line
        contactline += "".join(subresv)
        midlist.append(contactline)
        self.outlist = midlist

        #     try:
        #         temp = timepattern.search(line).groups()
        #     except AttributeError:
        #         sublist.append(line)
        #         subresv = sublist
        #         continue

        #     contactline = "[" + temp[0] + "]" +\
        #                   "".join(sublist[:-1]) +\
        #                   "[" + temp[1] + "]"
        #     sublist = []
        #     midlist.append(contactline)
        #     contactline = line
        # contactline = "[" + temp[0] + "]" +\
        #               "".join(subresv) +\
        #               "[" + temp[1] + "]"
        # midlist.append(contactline)
        # self.outlist = midlist

    def __SUBparser(self):
        """parser for *.sub"""
        print "Sub Format Detected."
        vfps = 23.98
        contactline = "{0}{%d}" % (int(vfps) * 2)
        midlist = []
        timepattern = re.compile(r'^\{(\d+)\}\{(\d+)\}')
        for line in self.cleansrc:
            if not timepattern.search(line):
                contactline += line
                continue
            midlist.append(contactline)
            contactline = line
        midlist.append(contactline)

        oldtime = ""
        oldte = "2000"
        timepattern = re.compile(r'^\{(\d+)\}\{(\d+)\}(.*)')
        for line in midlist:
            temp = timepattern.search(line).groups()
            sec = ["%.3f" % (int(x) / vfps) for x in temp[0:2]]
            st = [GetInHMS(float(ss)) for ss in sec]
            nline = "[" + st[0] + "]" + temp[2]
            if float(oldte) + 1 < float(sec[0]):
                self.outlist.append(oldtime)
            self.outlist.append(nline)
            oldte = sec[1]
            oldtime = "[" + st[1] + "]"
        self.outlist.append(oldtime)

    def regulator(self, pattern):
        print "Input Rgulated."
        contactline = ""
        midlist = []
        timepattern = re.compile(pattern)
        for line in self.cleansrc:
            if not timepattern.search(line):
                contactline += line
                continue
            midlist.append(contactline)
            contactline = line
        midlist.append(contactline)
        return midlist


def GetInHMS(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(int(m), 60)
    return "%02d:%02d:%05.2f" % (h, m, s)
#datetime.timedelta


def usage():
    print __doc__


if __name__ == "__main__":
    try:
        argv = sys.argv[1]
    except IndexError:
        usage()
        sys.exit(2)
    d = subtitleconv(argv)
