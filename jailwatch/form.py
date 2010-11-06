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

import random
import hashlib
import datetime

class Form(object):
    
    def __init__(self, name, ip):
        random.seed()
        self._name = str(name)
        self._token = hashlib.sha256(str(random.getrandbits(256)) + str(datetime.datetime.now()) + str(ip) + str(name)).hexdigest()
        
    @property
    def name(self):
        return self._name
    
    @property
    def token(self):
        return self._token
    
    

def register(form_name, session, request):
    frm = Form(form_name, request.remote.ip)
    session['nextform'] = frm
    return frm.token


def verify(form_name, token, session):
    frm = session.get('nextform')
    session['nextform'] = None
    if frm:
        if (frm.name == form_name) and (frm.token == token):
            return True
    return False

