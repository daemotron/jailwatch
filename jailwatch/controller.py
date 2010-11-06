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

import cherrypy
from jailwatch import template
from jailwatch import form
from jailwatch import auth

class Root(object):
    
    @cherrypy.expose
    @cherrypy.tools.auth()
    @template.output('main.html')
    def index(self):
        return template.render()


    @cherrypy.expose
    @template.output('login.html')
    def login(self, username=None, password=None, csrf_token=None):
        if cherrypy.request.method == 'GET':
            return template.render(login_error = False, csrftoken = form.register("login", cherrypy.session, cherrypy.request))
        elif cherrypy.request.method == 'POST':
            if form.verify("login", csrf_token, cherrypy.session) == False:
                raise cherrypy.HTTPError(status=500, message='Detected an attempt of a cross site request forgery attack')
            if auth.login(username, password, cherrypy.session) == True:
                url = cherrypy.session.get('login_url')
                if url == None:
                    url = "/"
                raise cherrypy.HTTPRedirect(url)
            return template.render(login_error = True, csrftoken = form.register("login", cherrypy.session, cherrypy.request))


    @cherrypy.expose
    def logout(self):
        auth.logout(cherrypy.session)
        raise cherrypy.HTTPRedirect('/')