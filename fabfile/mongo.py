from fabric.api import task, local, settings
from pprint import pprint
from cloudmesh.cm_mongo import cm_mongo
from cloudmesh.config.cm_config import cm_config, cm_config_server
from cloudmesh.user.cm_userLDAP import cm_userLDAP
from cloudmesh.pbs.pbs_mongo import pbs_mongo
from cloudmesh.util.util import path_expand
from cloudmesh.util.util import banner
from cloudmesh.util.util import yn_choice
from cloudmesh.inventory import Inventory
from cloudmesh.user.cm_template import cm_template
from cloudmesh.config.ConfigDict import ConfigDict

import yaml
import sys
import os.path

def get_pid(command):
    lines = local("ps -ax |fgrep {0}".format(command), capture=True).split("\n")
    pid = None
    for line in lines:
        if not "fgrep" in line:
            pid = line.split(" ")[0]
            break
    return (pid, line)

@task
def admin():
    """creates a password protected user for mongo"""

    config = cm_config_server().get("cloudmesh.server.mongo")

    user = config["username"]
    password = config["password"]

    #
    # setting up the list of dbs
    #
    dbs = set()
    print config["collections"]
    for collection in config["collections"]:
        dbs.add(config['collections'][collection]['db'])

    # setting the admin user
    script = []
    script.append('db.addUser("{0}", "{1}");'.format(user, password))
    script.append('db.auth("{0}", "{1}");'.format(user, password))

    # setting a password for each db

    for db in dbs:
        script.append('db = db.getSiblingDB("{0}");'.format(db))
        script.append('db.addUser("{0}", "{1}");'.format(user, password))
    script.append("use admin;")
    script.append('db.shutdownServer();')

    mongo_script = '\n'.join(script)

    print mongo_script
    local("echo -e '{0}' | mongo".format(mongo_script))

    print "USER", user
    print "PASSWORD", password

@task
def wipe():
    """wipes out all traces from mongo"""
    kill()
    config = cm_config_server().get("cloudmesh.server.mongo")

    path = path_expand(config["path"])

    banner("{0}".format(path))
    local("mkdir -p {0}".format(path))
    result = local("ls {0}".format(path), capture=True)
    if ''.join(result.split("\n")) is '':
        print "directory is empty"
    else:
        local("ls {0}".format(path))

    print 70 * "-"
    if yn_choice("deleting the directory", default="n"):
        local("rm -rf {0}".format(path))
        local("mkdir -p {0}".format(path))
        banner("{0}".format(path))
        local("ls {0}".format(path))

@task
def boot():
    # wipe mongo
    wipe()
    # kill mongo
    kill()
    # start mongo without auth
    start(auth=False)
    # create users
    admin()
    # restart with auth
    start(auth=True)

    config = cm_config_server().get("cloudmesh.server.mongo")
    path = path_expand(config["path"])

    local("ls {0}".format(path))

@task
def start(auth=True):
    '''
    start the mongod service in the location as specified in
    ~/.futuregrid/cloudmesh_server.yaml
    '''
    config = cm_config_server().get("cloudmesh.server.mongo")

    path = path_expand(config["path"])
    port = config["port"]

    if not os.path.exists(path):
        print "Creating mongodb directory in", path
        local("mkdir -p {0}".format(path))

    try:
        lines = local("ps -ax |grep '[m]ongod.*port {0}'".format(port), capture=True).split("\n")
    except:
        lines = []
    if lines:
        pid = lines[0].split(" ")[0]
        print "mongo already running in pid {0} for port {1}".format(pid, port)
    else:
        print "Starting mongod"
        with_auth = ""
        if auth:
            with_auth = "--auth"

        local("mongod {2} --fork --dbpath {0} --logpath {0}/mongodb.log --port {1}".format(path, port, with_auth))

@task
def clean():
    port = cm_config_server().get("cloudmesh.server.mongo.port")
    result = local('echo "show dbs" | mongo --quiet --port {0}'.format(port), capture=True).splitlines()
    for line in result:
        name = line.split()[0]
        local('mongo {0} --port {1} --eval "db.dropDatabase();"'.format(name, port))


@task
def inventory():
    mesh_inventory = Inventory()
    mesh_inventory.clear()
    mesh_inventory.generate()
    mesh_inventory.info()

@task
def info():
    (pid, line) = get_pid("mongod")
    print line


@task
def kill():
    stop()

@task
def stop():
    '''
    stops the currently running mongod
    '''
    # for some reason shutdown does not work
    # local("mongod --shutdown")
    (pid, line) = get_pid("mongod")
    if pid is None:
        print "No mongod running"
    else:
        print "Kill mongod"
        local ("killall -9 mongod")

@task
def vms_find():
    c = cm_mongo()
    c.activate()
    pprint (c.servers())

@task
def cloud():
    '''
    puts a snapshot of users, servers, images, and flavors into mongo
    '''
    clean()
    c = cm_mongo()
    c.activate()
    c.refresh(types=['users', 'servers', 'images', 'flavors'])
    ldap()
    inventory()

@task
def simple():
    '''
    puts a snapshot of servers, images, and flavors into mongo (no users)
    '''
    clean()
    c = cm_mongo()
    c.activate()
    c.refresh(types=['servers', 'images', 'flavors'])
    inventory()

@task
def metric():
    """puts an example of a log file into the mongodb logfile"""
    log_file = path_expand("~/.futuregrid/metric/sierra-sample.log")
    # create the mongo object
    # parse the log file
    # put each log information into the mongodb (or an obkject an than to mongodb)
    # maybe you do not need to parese log files for openstack but just read it from sql???

@task
def errormetric():
    """puts an example of a log file into the mongodb logfile"""
    # create the mongo object
    # parse the log file
    # put each error form the sql databse in toit


@task
def users():
    '''
    puts a snapshot of the users into mongo
    '''
    c = cm_mongo()
    c.activate()
    c.refresh(types=['users'])

@task
def cloudusers():
    '''adds the clud user information from FG to the users mongo info'''
    # to be done by hyungro
    user = cm_user()
    # hyungro



@task
def ldap():
    '''
    fetches a user list from ldap and displays it
    '''

    idp = cm_userLDAP ()
    idp.connect("fg-ldap", "ldap")
    idp.refresh()

    users = idp.list()

    print ("Fetching {0} Users from LDAP".format(len(users)))

'''
@task
def fg():
    """create a simple testbed"""
    start()
    local("python webui/fg.py")    
'''

@task
def projects():
    print "NOT IMPLEMENTED YET"
    print "this class will when finished be able to import project titles and description from the fg portal"


@task
def pbs(host, type):
    pbs = pbs_mongo()

    # get hpc user

    config = cm_config()
    user = config.config["cloudmesh"]["hpc"]["username"]


    pbs.activate(host, user)

    print "ACTIVE PBS HOSTS", pbs.hosts

    if host is None:
        hosts = pbs.hosts
    else:
        hosts = [host]

    if type is None:
        types = ['qstat', 'nodes']
    else:
        types = [type]

    d = []

    for host in hosts:
        for type in types:
            if type in  ["qstat", "queue", "q"]:
                d = pbs.get_pbsnodes(host)
            elif type in ["nodes"]:
                d = pbs.refresh_pbsnodes(host)

    for e in d:
        print "PBS -->"
        pprint(e)

