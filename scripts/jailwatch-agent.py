#!/usr/bin/env python

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
import re
import plistlib
import cPickle
import subprocess
import xml.parsers.expat
from optparse import OptionParser

JAILLIST = None
PROCLIST = None
SOCKLIST = None


def load_jail_list():
    global JAILLIST
    jails = {}
    jls = subprocess.Popen(["/usr/sbin/jls"], stdout=subprocess.PIPE).communicate()[0].splitlines()[1:]
    for line in jls:
        jl = line.split()
        hostname = subprocess.Popen(['/usr/sbin/jls', '-n', '-j', str(jl[0]), 'host.hostname'], stdout=subprocess.PIPE).communicate()[0].split('=')[1].strip()
        jails[jl[1]] = {'jid': int(jl[0]), 'hostname': hostname}
    JAILLIST = jails


def load_process_list():
    global PROCLIST
    processes = {}
    pcs = subprocess.Popen(['ps', 'axww', '-o', 'pid,jid,args'], stdout=subprocess.PIPE).communicate()[0].splitlines()[1:]
    for line in pcs:
        ps = line.split()
        jid = int(ps[1])
        pid = int(ps[0])
        if not jid in processes.keys():
            processes[jid] = {}
        processes[jid][pid] = " ".join(ps[2:])
    PROCLIST = processes


def check_process(jid, pid=None, process=None):
    global PROCLIST
    if pid:
        try:
            return pid in PROCLIST[jid].keys()
        except:
            return False
    elif process:
        try:
            rg = re.compile(re.escape(process))
            for value in PROCLIST[jid].values():
                if rg.match(value):
                    return True
        except:
            return False
        return False
    else:
        return False


def get_jid(pid):
    global PROCLIST
    for jid in PROCLIST.keys():
        if pid in PROCLIST[jid].keys():
            return jid
    return None


def load_socket_lists():
    global SOCKLIST
    socketlist = {'tcp': {}, 'udp': {}, 'unix': {}}
    socks = subprocess.Popen(['/usr/bin/sockstat', '-4', '-6', '-u', '-l'], stdout=subprocess.PIPE).communicate()[0].splitlines()[1:]
    for line in socks:
        sock = line.split()
        pid = int(sock[2])
        jid = get_jid(pid)
        
        if 'tcp' in sock[4]:
            type = 'tcp'
        elif 'udp' in sock[4]:
            type = 'udp'
        elif 'dgram' in sock[4] or 'stream' in sock[4]:
            type = 'unix'
        else:
            type = None
        
        if type == 'tcp' or type == 'udp':
            port = int(sock[5].split(':')[-1])
        elif type == 'unix':
            port = sock[5].strip()
        
        if type:
            if not jid in socketlist[type].keys():
                socketlist[type][jid] = []
            socketlist[type][jid].append(port)
    SOCKLIST = socketlist


def check_socket(jid, proto, socket):
    global SOCKLIST
    try:
        return socket in SOCKLIST[proto][jid]
    except:
        return False


def check_service(jid, up, service, serv_conf):
    result = {}
    if 'processes' in serv_conf.keys():
        tmp = {}
        for process in serv_conf['processes']:
            if up:
                tmp[process] = check_process(jid, process=process)
            else:
                tmp[process] = False
        result['processes'] = tmp
    if 'tcp-ports' in serv_conf.keys():
        tmp = {}
        for port in serv_conf['tcp-ports']:
            if up:
                tmp[port] = check_socket(jid, 'tcp', port)
            else:
                tmp[port] = False
        result['tcp-ports'] = tmp
    if 'udp-ports' in serv_conf.keys():
        tmp = {}
        for port in serv_conf['udp-ports']:
            if up:
                tmp[port] = check_socket(jid, 'udp', port)
            else:
                tmp[port] = False
        result['udp-ports'] = tmp
    if 'unix-sockets' in serv_conf.keys():
        tmp = {}
        for port in serv_conf['unix-sockets']:
            if up:
                tmp[port] = check_socket(jid, 'unix', port)
            else:
                tmp[port] = False
        result['unix-sockets'] = tmp
    return result


def process_configuration(conf_object):
    global JAILLIST
    result = {}
    for key in conf_object.keys():
        tmp = {}
        tmp['ip'] = conf_object[key]['ip']
        
        # Is the jail up and running?
        if tmp['ip'] in JAILLIST.keys():
            tmp['up'] = True
            tmp['jid'] = JAILLIST[tmp['ip']]['jid']
        else:
            tmp['up'] = False
            tmp['jid'] = None
        
        # Detect service availability
        tmp['services'] = {}
        for service in conf_object[key]['services'].keys():
            tmp['services'][service] = check_service(tmp['jid'], tmp['up'], service, conf_object[key]['services'][service])
        result[key] = tmp
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
    
    # Prepare system to work
    load_jail_list()
    load_process_list()
    load_socket_lists()
    
    # Load configuration and execute checks
    cfg_obj = read_configfile(options.configfile)
    res_obj = process_configuration(cfg_obj)
    write_result(res_obj, options.resultfile)


if __name__ == '__main__':
    main()
