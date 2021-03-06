
#from cloudmesh_common.logger import LOGGER
from cloudmesh.cm_mongo import cm_MongoBase
from cloudmesh.config.cm_config import cm_config
from cloudmesh.config.ConfigDict import ConfigDict
from cloudmesh.user.cm_user import cm_user
import os
from pprint import pprint
import json

# ----------------------------------------------------------------------
# SETTING UP A LOGGER
# ----------------------------------------------------------------------

#log = LOGGER(__file__)

class cm_experiment_db(cm_MongoBase):
    """
    This methods holds some status information that is associated with a web
    page
    """

    cm_kind = 'experiment'

    def __init__(self):
        self.cm_type = "experiment"
        self.connect()

    def delete(self, user, experiment=None):
        '''
        Deletes the state values associated with a experiment. If non is specified for
        experiment all experiment state values are deleted

        :param user: the user for which the state values are recorded
        :type user: string
        :param experiment: the experiment base url
        :type experiment: of the form /uri (string)
        '''

        if experiment is None:
            self.db_mongo.remove({"cm_type" : self.cm_type,
                                  "cm_user_id": user})
        else:
            self.db_mongo.remove({"cm_type" : self.cm_type,
                                  "experiment": experiment,
                                  "cm_user_id": user})

    def add(self, user, experiment, attribute, value):
        '''
        adds the state value for a user and experiment

        :param user:
        :type user:
        :param experiment:
        :type experiment:
        :param attribute:
        :type attribute:
        :param value:
        :type value:
        '''

        self.update({
                     'cm_kind': self.cm_kind,
                     'cm_user_id': user,
                     'experiment': experiment,
                     'attribute': attribute
                    }, {
                     'cm_kind': self.cm_kind,
                     'cm_user_id': user,
                     'experiment': experiment,
                     'attribute': attribute,
                     'value': value})

    def get(self, user, experiment, attribute):
        '''
        get the state value for a user and a experiment

        :param user:
        :type user:
        :param experiment:
        :type experiment:
        :param attribute:
        :type attribute:
        '''
        result = m.find_one({'cm_user_id': user,
                             'experiment': experiment,
                             'attribute': attribute})
        return result['value']

    def getUserData(self):
         userinfo = cm_user().info('psjoshi')
         configuration = cm_config()
         return configuration['cloudmesh']['experiment']

if __name__ == "__main__":


    m = cm_experiment_db()
    m.clear()


    m.add('gregor', 'exp1', 'VMs', '100')
    m.add('gregor', 'exp1', 'images', '99')

    m.add('gregor', 'exp1', 'dict', {"a": 1, "b": {"c": 1}})


    cursor = m.find({})

    userinfo = cm_user().info('psjoshi')
    configuration = cm_config()
    #pprint(configuration['cloudmesh']['experiment'])

    '''
    for element in cursor:
        print 'element', element


    print m.get('gregor', 'exp1', 'VMs')
    print m.get('gregor', 'exp1', 'images')
    print m.get('gregor', 'exp1', 'dict')

    pprint(m.get('gregor', 'exp1', 'dict')['b'])
    '''


