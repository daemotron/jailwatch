#!/usr/bin/env python2

# Copyright (c) 2010 Daemotron <mail@daemotron.net>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import os
import sys
import plistlib
import cPickle
import subprocess
import xml.parsers.expat
from optparse import OptionParser

def get_jail_list():
    jails = []
    jls = subprocess.Popen(["/usr/sbin/jls"], stdout=subprocess.PIPE).communicate()[0].splitlines()[1:]
    for line in jls:
        jails.append(line.split())
    return jails

def process_configuration(conf_object):
    result = {}
    for key in conf_object.keys():
        # TODO: insert detection routines here
        pass
    return result

def write_result(result_object, outfile):
    try:
        outfd = open(outfile, 'wb')
    except IOError as e:
        sys.stderr.write("IOError: [Errno %d] %s: %s\n" % (e.errno, e.strerror, configfile))
        sys.exit(1)
    
    try:
        cPickle.dump(result_object, outfd, cPickle.HIGHEST_PROTOCOL)
    except pickle.PicklingError as e:
        sys.stderr.write("Internal Data Format Error: [Errno %d] %s\n" % (e.errno, e.strerror))
        outfd.close()
        sys.exit(1)
    
    outfd.close()
    

def read_configfile(configfile=None):
    if configfile:
        try:
            conf = plistlib.readPlist(configfile)
        except IOError as e:
            sys.stderr.write("IOError: [Errno %d] %s: %s\n" % (e.errno, e.strerror, configfile))
            sys.exit(1)
        except xml.parsers.expat.ExpatError as e:
            sys.stderr.write("Invalid file format: could not read configuration from %s.\n" % configfile)
            sys.exit(1)
        
        return plistlib.readPlist(configfile)
    else:
        return None

def main():
    parser = OptionParser("%s [options]" % os.path.basename(sys.argv[0]))
    parser.add_option("-c", "--conf", dest="configfile", default="/etc/jailwatch/agent.conf", help="use indicated configuration file")
    parser.add_option("-o", "--out", dest="resultfile", default="/var/jailwatch/status.db", help="write detected status to indicated file")
    (options, args) = parser.parse_args()
    
    cfg_obj = read_configfile(options.configfile)
    res_obj = process_configuration(cfg_obj)
    write_result(res_obj, options.resultfile)


if __name__ == '__main__':
    main()
