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
import cherrypy

jailwatch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, jailwatch_path)

cherrypy.config.update(sys.argv[1])

from jailwatch.controller import Root

cherrypy.config.update({'tools.staticdir.root': os.path.join(str(cherrypy.config.get('theme.dir')), str(cherrypy.config.get('theme.name')), 'static')})
cherrypy.quickstart(Root(), '/', {'/static': {
          'tools.staticdir.on': True,
          'tools.staticdir.dir': "",
      }})