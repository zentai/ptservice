#!/usr/local/bin/python
import sys
import cherrypy
import os
import logging.config
import yaml

def setup_logging(default_path='logging.yaml', default_level=logging.DEBUG, env_key='LOG_CFG'):
    """
	Setup logging configuration
    """
    print "setup logging"
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

from ptservice import *
class Root:
    logger = logging.getLogger(__name__)
    member = MemberManager()
    @cherrypy.expose
    def index(self):
            return 'Hello, this is your default site.'

setup_logging()
# setup_celery()
cherrypy.config.update({
'environment': 'production',
'log.screen': False,
'server.socket_host': '127.0.0.1',
'server.socket_port': 8080,
})

cherrypy.quickstart(Root())
settings = { 
 'global': {
    'server.socket_port' : 8080,
    'server.socket_host': "",
    'server.socket_file': "",
    'server.socket_queue_size': 5,
    'server.protocol_version': "HTTP/1.0",
    'server.log_to_screen': True,
    'server.log_file': "",
    'server.reverse_dns': False,
    'server.thread_pool': 10,
    'server.environment': "development"
 },
 '/service/xmlrpc' : {
    'xmlrpc_filter.on': True
 },
 '/admin': {
    'session_authenticate_filter.on' :True
 },
 '/css/default.css': {
    'static_filter.on': True,
    'static_filter.file': "data/css/default.css"
 }
}
cherrypy.config.update(settings)