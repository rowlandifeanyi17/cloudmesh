""" run with

nosetests -v --nocapture

or

nosetests -v

individual tests can be run with

nosetests -v  --nocapture test_cm_compute.py:Test.test_06

"""

from sh import head
from sh import fgrep
import string
import os
import time


from cloudmesh.config.cm_config import cm_config
from cloudmesh.iaas.openstack.cm_compute import openstack
from cloudmesh.util.cm_table import cm_table
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

from cloudmesh.util.util import HEADING


class Test:

    # assuming first - is the prefered cloud
    print os.path.expandvars("$HOME/.futuregrid/cloudmesh.yaml")
    cloud_label = head(
        fgrep("-", os.path.expandvars("$HOME/.futuregrid/cloudmesh.yaml")), "-n", "1")
    cloud_label = cloud_label.replace(" - ", "").strip()

    def setup(self):
        self.configuration = cm_config()
        self.name = self.configuration.active()[0]
        print "ACTIVE CLOUD", self.name
        self.cloud = openstack(self.name)
        self.cloud.get_token()
        print "LOADED CLOUD"

    def tearDown(self):
        pass

    def test_get_extensions(self):
        HEADING()
        
        print json.dumps(self.cloud.get_extensions(), indent=4)
        assert True

    def test_get_users(self):
        HEADING()
        
        self.cloud.refresh("users")
        
        #        print json.dumps(self.cloud.get_users(), indent=4)
        print json.dumps(self.cloud.users, indent=4)
        
        assert True
    
    def test_get_limits(self):
        HEADING()
        print json.dumps(self.cloud.get_limits(), indent=4)
        assert True

    def test_get_servers(self):
        HEADING()

        print json.dumps(self.cloud.get_servers(), indent=4)
        assert True

    def test_get_flavors(self):
        HEADING()
        #self.cloud.refresh('flavors')
        #print json.dumps(self.cloud.dump('flavors'), indent=4)

        print json.dumps(self.cloud.get_flavors(), indent=4)
        assert True

    def test_get_images(self):
        HEADING()
        self.cloud.refresh('images')
        print json.dumps(self.cloud.dump('images'), indent=4)

        print json.dumps(self.cloud.get_images(), indent=4)
        assert True

    def test_00_label(self):
        HEADING()
        print self.cloud_label
        assert self.cloud.label == self.cloud_label

    def test_01_limit(self):
        HEADING()
        print json.dumps(self.cloud.limits(), indent=4)

    def test_02_info(self):
        HEADING()
        self.cloud.refresh('images')
        print json.dumps(self.cloud.dump('images'), indent=4)
        # pp.pprint(self.cloud.dump('images', with_manager=True))
        pp.pprint(self.cloud.images)
        # doing a simple test as tiny is usually 512
        # assert self.cloud.flavors['m1.tiny']['ram'] == 512
        print "Currently running vms:", len(self.cloud.images)
        # we assume cloud is always busy which may actually not true
        # we shoudl start our own vm and than probe for it for now > 0 will do
        assert self.cloud.images > 0

    def test_03_flavors(self):
        HEADING()
        self.cloud.refresh('flavors')
        print json.dumps(self.cloud.dump('flavors'), indent=4)

        
        # doing a simple test as tiny is usually 512
        assert self.cloud.flavors['m1.tiny']['ram'] == 512

    def test_04_start_vm(self):
        HEADING()
        configuration = cm_config()
        image = configuration.default(self.name)['image']
        keys = configuration.userkeys()
        key_name = keys["default"]
        key_content = keys["keylist"][key_name]
        #print key_name
        #print key_content
        print "STARTING IMAGE", image
        meta = {"cmtag":"testing tag from creation via rest api"}
        result = self.cloud.vm_create("fw-test-by-post-003", "2", image, key_name="grizzlykey",meta=meta)
        pp.pprint(result)
        assert len(result.keys()) > 0

    def test_04_get_public_ip(self):
        HEADING()
        print "Obtaining public ip......"
        ip = self.cloud.get_public_ip()
        print "this is the ip returned:--->%s<---" % ip
    
    def test04_assign_public_ip(self):
        HEADING()
        print "Associate a public ip to an running instance......"
        #serverid = "cc9bd86b-babf-4760-a5cd-c1f28df7506b"
        #ip = "fakeip" # {u'itemNotFound': {u'message': u'floating ip not found', u'code': 404}}
        #ip = "198.202.120.175"
        serverid = "b088e764-681c-4448-b487-9028b23a729e"
        print "In process of obtaining a new ip..."
        ip = self.cloud.get_public_ip()
        print "Got a new ip as: %s, now associating the ip..." % ip
        print self.cloud.assign_public_ip(serverid,ip)

    def test04_list_public_ips(self):
        HEADING()
        print "List all public ips allocated to the current account..."
        ips = self.cloud.list_allocated_ips()
        ips_id_to_instance = {}
        for ip in ips:
            ips_id_to_instance[ip['id']] = ip['instance_id']
        print ips_id_to_instance

    def test04_release_public_ips(self):
        HEADING()
        print "Release all public ips allocated to the current account but not being used..."
        print "Before releasing, we have..."
        self.test04_list_public_ips()
        print "releasing..."
        self.cloud.release_unused_public_ips()
        print "after releasing..."
        self.test04_list_public_ips()
                        
    def test_05_print_vms(self):
        HEADING()
        self.cloud.refresh('servers')
        print json.dumps(self.cloud.dump('servers'), indent=4)
        # we assume that there are always images running
        assert len(self.cloud.servers) > 0

    def test_06_refresh(self):
        HEADING()
        self.cloud.refresh()
        pp.pprint(self.cloud.get(self.name))
        assert self.cloud.images > 0

    """
    def test_0??_usage(self):
        result = self.cloud.usage("2000-01-01T00:00:00", "2013-12-31T00:00:00")
        print json.dumps(result, indent=4)
        assert ['Instances'] > 0
    """

    def test_07_print_tables(self):
        HEADING()
        self.test_03()
        table = cm_table()
        columns = ["id", "name", "ram", "vcpus"]

        table.create(self.cloud.flavors, columns, header=True)
        print table

        table = cm_table()
        columns = ["id", "name", "ram", "vcpus"]

        table.create(self.cloud.flavors, columns, format='HTML', header=True)
        print table

        table = cm_table()
        columns = ["id", "name", "ram", "vcpus"]

        table.create(self.cloud.flavors, columns, format='%12s', header=True)
        print table

        assert table is not None

    def test_07_start_delete_vm(self):
        print "no test was being done"
        '''
        name ="%s-%04d" % (self.cloud.credential["OS_USERNAME"], 1)
        out = self.cloud.vm_create(name, "m1.tiny", "6d2bca76-8fff-4d57-9f29-50378539b4fa")

        pp.pprint(out)
        print json.dumps(out, indent=4)

        key = out.keys()[0]
        id = out[key]["id"]
        print id
        '''
        #id = "d9e73d16-a85e-47bf-8ab4-19d7955622db"
        #id = "2a00332d-6a4a-4f7e-ad46-751438cc4d5e"
        #id = "af46b3cd-99d9-4609-8c27-c481b0227e15"
        #id="fakeid"
        #id="b1279fa1-390a-41f8-b5d2-ad9b26cfb48a"
        #ret=self.cloud.vm_delete(id)
        #print "--->%s<---" % ret

    def test_08_delete_vms_of_user(self):
        HEADING()

        self.cloud.refresh()

        user_id = self.cloud.find_user_id(force=True)
        vm_ids = self.cloud.find('user_id', user_id)
        print "userid", user_id
        config = cm_config()
        config.data['cloudmesh']['clouds'][self.name][
            'credentials']['OS_USER_ID'] = user_id
        config.write()

        #
        # delete all vms of the user
        #
        servers = self.cloud.servers
        print servers

        list = self.cloud.vms_delete_user()

        self.cloud = openstack(self.cloud_label)
        self.cloud.refresh()
        self.cloud.info()

        vm_ids = self.cloud.find('user_id', user_id)
        self.cloud.info()

        time.sleep(2)
        self.cloud.refresh()

        while len(vm_ids) > 0:
            vm_ids = self.cloud.find('user_id', user_id)
            self.cloud.refresh("servers")
            self.cloud.info()
            time.sleep(1)

        print "vms",  vm_ids

        assert vm_ids == []

    def test_09_start_two_vms(self):
        HEADING()
        configuration = cm_config()
        image = configuration.default(self.name)['image']
        print "STARTING IMAGE", image
        result = self.cloud.vm_create("gregor-test-001", "m1.tiny", image)
        # print result
        result = self.cloud.vm_create("gregor-test-002", "m1.tiny", image)
        # print result
        self.cloud.refresh()
        self.cloud.info()

        config = cm_config()
        print "CONFIG"
        user_id = config.data['cloudmesh']['clouds'][
            self.name]['credentials']['OS_USER_ID']
        print user_id

        vm_ids = self.cloud.find('user_id', user_id)
        print vm_ids

        assert len(vm_ids) == 2

    def test_10_list_user_vms(self):
        HEADING()
        list = self.cloud.vms_user(refresh=True)
        pp.pprint(list)

    def test_11_refresh_all(self):
        HEADING()
        self.cloud.refresh()
        self.cloud.info()

    def test_12_print_states(self):
        HEADING()
        self.cloud.refresh()
        print self.cloud.states

        search_states = ('ACTIVE', 'PAUSED')

        state = 'ACTIVE'
        userid = None

        print state in search_states

        # self.cloud.display(search_states, userid)

        # print json.dumps(self.cloud.servers, indent=4)

        self.cloud.display_regex("vm['status'] in ['ACTIVE']", userid)

        print json.dumps(self.cloud.dump('servers'), indent=4)

        #        self.cloud.display_regex("vm['status'] in ['ERROR']", userid)

        # print json.dumps(self.cloud.servers, indent=4)

    def test_13_meta(self):
        HEADING()
        self.clean()
        image = self.configuration.default(self.name)['image']
        flavor = self.configuration.default(self.name)['flavor']
        self.configuration.prefix = "gvonlasz-test"
        self.configuration.incr()
        name = self.configuration.vmname
        print name
        result = self.cloud.vm_create(name, flavor, image)
        id = result['id']
        print id
        result = self.cloud.wait(id, 'ACTIVE')
        result = self.cloud.set_meta(id, {"owner": "gregor"})
        print "RESULT", result
        meta = self.cloud.get_meta(id)
        print meta

    def start(self):
        HEADING()
        image = self.configuration.default(self.name)['image']
        flavor = self.configuration.default(self.name)['flavor']
        self.configuration.prefix = "gvonlasz-test"
        self.configuration.incr()
        name = self.configuration.vmname
        print "STARTING IMAGE", name, image, flavor
        result = self.cloud.vm_create(name, flavor, image)
        print result

    def info(self):
        HEADING()
        self.cloud.refresh()
        self.cloud.info()

    def clean(self):
        HEADING()

        self.cloud.refresh()
        self.cloud.info()

        user_id = self.cloud.find_user_id()
        print "Cleaning", user_id

        list = self.cloud.vms_delete_user()
        print "Cleaning", list

        vm_ids = self.cloud.find('user_id', user_id)
        while len(vm_ids) > 0:
            vm_ids = self.cloud.find('user_id', user_id)
            self.cloud.refresh("servers")
            self.cloud.info()
            time.sleep(1)

        print "vms",  vm_ids

        assert vm_ids == []