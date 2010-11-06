=========
Jailwatch
=========
----------------------------
Keeping an Eye on your Jails
----------------------------

About Jailwatch
===============

Jailwatch is a simple monitoring solution specialized in status monitoring of
`FreeBSD <http://www.freebsd.org/>`_
`jails <http://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/jails.html>`_
and services kept within such a jail.

Features
--------

* Data collection
  
  * no agent daemon required
  
  * driven by simple cron jobs
  
* Web interface
  
  * WSGI-compliant web application
  
  * authenticates agains LDAP
  
  * customization of look & feel via CSS and `Genshi <http://genshi.edgewall.org>`_ templates


Behind the scenes
=================

Jailwatch is implemented in `Python <http://www.python.org/>`_. The web interface
makes use of `CherryPy <http://www.cherrypy.org/>`_ , `Genshi <http://genshi.edgewall.org>`_
and the `python-ldap <http://www.python-ldap.org/>`_ library.
