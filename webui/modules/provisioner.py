from flask import Blueprint
from flask import Flask, render_template, request, redirect, flash, url_for
from cloudmesh.config.cm_keys import cm_keys
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import TextField, SelectField
from cloudmesh.inventory.inventory import FabricImage, FabricServer, \
    FabricService, Inventory
from hostlist import expand_hostlist
from cloudmesh.provisioner.provisioner import *
from cloudmesh.inventory.inventory import PROVISIONING_CHOICES
from cloudmesh.provisioner.queue.celery import celery
from cloudmesh.provisioner.queue.tasks import info, provision
from pprint import pprint
    
provisioner_module = Blueprint('provisioner_module', __name__)


inventory = Inventory("nosetest")

# ============================================================
# PROVISINOR
# ============================================================
provisionerImpl = ProvisionerSimulator
provisioner = provisionerImpl()

@provisioner_module.route('/provision/summary/')
def display_summary():
    
    queue = celery.control.inspect()



    """
    for j in range(10):
    print chr(27) + "[2J"
    inventory.print_cluster("bravo")
    for host in hosts:
        print host, t[host].status
    pprint (i.active())
    pprint (i.scheduled())
    pprint (i.reserved())
    time.sleep(1)
    """
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return render_template('provision_summary_table.html',
                           provisioner=provisioner,
                           queue=queue,
                           updated=time_now)

class ProvisionForm(Form):

    clusters = [cluster.name for cluster in inventory.get("cluster")]
    choices = zip (clusters, clusters)
    cluster = SelectField("Cluster", choices=choices)
    nodespec = TextField("Nodes")
    provision_choices = zip(PROVISIONING_CHOICES,PROVISIONING_CHOICES)
    service = SelectField("Service", choices=provision_choices)

    def validate(self):
        cluster = inventory.get("cluster", self.cluster.data)
        posibilities = expand_hostlist(cluster.definition)
        choice = expand_hostlist(self.nodespec.data)
        if choice == []:
            ok = False
        else:
            ok = set(choice).issubset(posibilities)
        print "Validate", ok, choice
        return ok

@provisioner_module.route("/provision/", methods=("GET", "POST"))
def display_provision_form():

    form = ProvisionForm(csrf=False)

    if form.validate_on_submit():
        flash("Success")
        print "FORM"
        pprint( form.__dict__)
        print "CLUSTER", form.cluster.data
        print "Service", form.service.data
        hosts = expand_hostlist(form.nodespec.data)
        print "Nodespec", hosts

        for host in hosts:
            print "PROVISION HOST", host
            provision.delay(host,form.service.data)

        return redirect("/provision/summary/")

    else:
        flash("Wrong submission")
    inventory.refresh()
    return render_template("provision.html", form=form, inventory=inventory)    
    
        
