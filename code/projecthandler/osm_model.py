#
#   Copyright 2017 CNIT - Consorzio Nazionale Interuniversitario per le Telecomunicazioni
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an  BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from __future__ import unicode_literals

import copy
import json
import os.path
import yaml
from lib.util import Util
import logging
from projecthandler.models import ProjectStateless

from lib.osm.osm_parser import OsmParser
from lib.osm.osm_rdcl_graph import OsmRdclGraph
from lib.osm.osmclient.client import Client

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('OsmModel.py')


PATH_TO_SCHEMAS = 'lib/osm/schemas/'
PATH_TO_DESCRIPTORS_TEMPLATES = 'lib/osm/descriptor_template'
DESCRIPTOR_TEMPLATE_SUFFIX = '.json'
GRAPH_MODEL_FULL_NAME = 'lib/TopologyModels/osm/osm.yaml'
EXAMPLES_FOLDER = 'usecases/OSM/'


class OsmProject(ProjectStateless):
    """Osm Project class
    The data model has the following descriptors:
        # descrtiptor list in comment #

    """

    def get_descriptors(self, type_descriptor):
        """Returns all descriptors of a given type"""
        log.debug("Get %s descriptors", type_descriptor)
        try:
            client = Client()
            if type_descriptor == 'nsd':
                result = client.nsd_list()
                print result
            elif type_descriptor == 'vnfd':
                result = client.vnfd_list()
                #print result

        except Exception as e:
            log.exception(e)
            result = {}
        return result

    def get_descriptor(self, descriptor_id, type_descriptor):
        """Returns a specific descriptor"""
        try:
            client = Client()
            if type_descriptor == 'nsd':
                result = client.nsd_get(descriptor_id)
                print result
            elif type_descriptor == 'vnfd':
                result = client.vnfd_get(descriptor_id)
                print result
        except Exception as e:
            log.exception(e)
            result = {}

        return result

    @classmethod
    def data_project_from_files(cls, request):

        file_dict = {}
        for my_key in request.FILES.keys():
            file_dict[my_key] = request.FILES.getlist(my_key)

        log.debug(file_dict)

        data_project = OsmParser.importprojectfiles(file_dict)

        return data_project

    @classmethod
    def data_project_from_example(cls, request):
        osm_id = request.POST.get('example-osm-id', '')
        data_project = OsmParser.importprojectdir(EXAMPLES_FOLDER + osm_id + '/JSON', 'yaml')
        return data_project

    @classmethod
    def get_example_list(cls):
        """Returns a list of directories, in each directory there is a project osm"""

        path = EXAMPLES_FOLDER
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        return {'osm': dirs}

    @classmethod
    def get_new_descriptor(cls, descriptor_type, request_id):

        json_template = cls.get_descriptor_template(descriptor_type)

        return json_template

    @classmethod
    def get_descriptor_template(cls, type_descriptor):
        """Returns a descriptor template for a given descriptor type"""

        try:
            schema = Util.loadjsonfile(os.path.join(PATH_TO_DESCRIPTORS_TEMPLATES, type_descriptor + DESCRIPTOR_TEMPLATE_SUFFIX))
            return schema
        except Exception as e:
            log.exception(e)
            return False

    @classmethod
    def get_clone_descriptor(cls, descriptor, type_descriptor, new_descriptor_id):
        new_descriptor = copy.deepcopy(descriptor)

        return new_descriptor

    def get_type(self):
        return "osm"

    def __str__(self):
        return self.name

    def get_overview_data(self):
        current_data = json.loads(self.data_project)
        result = {
            'owner': self.owner.__str__(),
            'name': self.name,
            'updated_date': self.updated_date.strftime('%Y-%m-%d %H:%M'),
            'info': self.info,
            'type': 'osm',
            'nsd': '#',#len(current_data['nsd'].keys()) if 'nsd' in current_data else 0,

            'vnfd': '#',#len(current_data['vnfd'].keys()) if 'vnfd' in current_data else 0,

            'validated': self.validated
        }

        return result

    def get_graph_data_json_topology(self, descriptor_id):
        rdcl_graph = OsmRdclGraph()
        project = self.get_dataproject()
        topology = rdcl_graph.build_graph_from_project(project,
                                                     model=self.get_graph_model(GRAPH_MODEL_FULL_NAME))
        return json.dumps(topology)

    def create_descriptor(self, descriptor_name, type_descriptor, new_data, data_type, file_uploaded):
        """Creates a descriptor of a given type from a json or yaml representation

        Returns the descriptor id or False
        """
        log.debug('Create descriptor')

        try:
            client = Client()
            if type_descriptor == 'nsd':
                result = client.nsd_onboard(file_uploaded)
            elif type_descriptor == 'vnfd':
                result = client.vnfd_onboard(file_uploaded)

            else:
                log.debug('Create descriptor: Unknown data type')
                return False

        except Exception as e:
            log.exception(e)
            result = False
        return result

    def delete_descriptor(self, type_descriptor, descriptor_id):
        log.debug('Delete descriptor')

        try:
            client = Client()
            if type_descriptor == 'nsd':
                result = client.nsd_delete(descriptor_id)
            elif type_descriptor == 'vnfd':
                result = client.vnfd_delete(descriptor_id)

            else:
                log.debug('Create descriptor: Unknown data type')
                return False

        except Exception as e:
            log.exception(e)
            result = False
        return result

    def set_validated(self, value):
        self.validated = True if value is not None and value == True else False

    def get_add_element(self, request):
        result = False

        return result

    def get_remove_element(self, request):
        result = False
        
        return result

    def get_add_link(self, request):

        result = False

        return result

    def get_remove_link(self, request):
        result = False

        return result


    def get_available_nodes(self, args):
        """Returns all available node """
        log.debug('get_available_nodes')
        try:
            result = []
            #current_data = json.loads(self.data_project)
            model_graph = self.get_graph_model(GRAPH_MODEL_FULL_NAME)
            for node in model_graph['layer'][args['layer']]['nodes']:

                current_data = {
                    "id": node,
                    "category_name": model_graph['nodes'][node]['label'],
                    "types": [
                        {
                            "name": "generic",
                            "id": node
                        }
                    ]
                }
                result.append(current_data)

            #result = current_data[type_descriptor][descriptor_id]
        except Exception as e:
            log.debug(e)
            result = []
        return result