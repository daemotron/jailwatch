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

import ldap
import cherrypy
import functools


class AuthStatus(object):
    
    def __init__(self, username=None, displayname=None, authenticated=False):
        self._authenticated = authenticated
        self._username = username
        self._displayname = displayname
        
    @property
    def authenticated(self):
        return self._authenticated
    
    @property
    def username(self):
        return self._username
    
    @property
    def displayname(self):
        return self._displayname



def auth_tool(allowed_groups=None, debug=False):
    stat = cherrypy.session.get('auth', None)
    if stat == None:
        cherrypy.session['login_url'] = "/" + "/".join(cherrypy.url().split('/')[3:])
        raise cherrypy.HTTPRedirect('/login', 307)
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', auth_tool)
    


def is_authenticated(session, url):
    stat = session.get('auth', None)
    if stat == None:
        session['login_url'] = url
        return False
    else:
        return True


def login(user, password, session):
    con = ldap.initialize(str(cherrypy.config.get('ldap.url')))
    if cherrypy.config.get('ldap.tls'):
        try:
            con.start_tls_s()
        except ldap.LDAPError as e:
            cherrypy.log(e.message['info'])
            return False
    try:
        con.simple_bind_s(str(cherrypy.config.get('ldap.template')) % user, password)
    except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM):
        return False
    base_dn = str(cherrypy.config.get('ldap.template'))[str(cherrypy.config.get('ldap.template')).find(',')+1:]
    filter = "(&(objectclass=inetOrgPerson)(uid=%s))" % user
    r = con.search_s(base_dn, ldap.SCOPE_SUBTREE, filter, ['cn'])
    if r:
        cn = r[0][1]['cn'][0]
    else:
        cn = user
    session['auth'] = AuthStatus(user, cn, True)
    con.unbind_s()
    return True


def logout(session):
    session['auth'] = None
    cherrypy.lib.sessions.expire()
    
    
def passwd(old_pw, new_pw, session):
    stat = session.get('auth', None)
    if stat == None:
        return False
    dn = str(cherrypy.config.get('ldap.template')) % stat.username
    con = ldap.initialize(str(cherrypy.config.get('ldap.url')))
    if cherrypy.config.get('ldap.tls'):
        try:
            con.start_tls_s()
        except ldap.LDAPError as e:
            cherrypy.log(e.message['info'])
            return False
    try:
        con.simple_bind_s(dn, old_pw)
    except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM):
        cherrypy.log(e.message['info'])
        return False
    try:
        con.passwd_s(dn, old_pw, new_pw)
    except:
        con.unbind_s()
        return False
    con.unbind_s()
    return True