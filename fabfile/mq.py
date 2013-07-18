from fabric.api import task, local, execute
import clean
import os
import sys
import platform
from cloudmesh.util.password import get_password, get_user, get_host

input = raw_input

__all__ = ['user','install','host','allow', 'check',"dns"]

@task
def install():
    """install the rabitmq"""
    if sys.platform == "darwin":
        local("brew install rabbitmq")
    else:
        print "ERROR: error no other install yet provided "
        sys.exit()

@task
def user(name=None):
    ''' create a user in rabit mq
    
    :param name: if the name is ommited it will be queried for it.
    '''
    if name is None: 
        user = get_user()
    password = get_password()
    local("rabbitmqctl {0} {1}".format(name,password))

@task
def host():
    """adding a host to rabitmq"""
    host = get_host()
    local("rabbitmqctl add_vhost {0}".format(host))

@task
def allow():
    """allow a user to access the host in rabitmq"""
    values = {
        'host': get_host(),
        'user': get_user()
        }
    #print('rabbitmqctl set_permissions -p {host} {user} ".*" ".*" ".*"'.format(**values))
    local('rabbitmqctl set_permissions -p {host} {user} ".*" ".*" ".*"'.format(**values))

@task
def check():
    values = {
        'host': platform.node(),
        'hostname': platform.node().replace(".local", ""),
        'file': '/etc/hosts'
        }
    result = int(local("fgrep {host} {file} | wc -l".format(**values), capture=True))
    if result == 0:
        print ('ERROR: the etc file "{file}" does not contain the hostname "{host}"'.format(**values))
        print
        print ("make sure to add a line such as")
        print
        print ("127.0.0.1       localhost {hostname} {host}".format(**values))
        print
        print ("make sure to restart the dns server after you changed the etc host file")
        print ("do this with fab mq.dns")

@task
def dns():
    local("dscacheutil -flushcache")
