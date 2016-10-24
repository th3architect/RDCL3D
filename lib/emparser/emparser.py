import json
import pyaml
import yaml
from util import Util
from t3d_util import T3DUtil
import logging
import traceback
import glob
import os

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('EmpLogger')


def importproject(dir_project, type):
    project = {
        'nsd': {},
        'vnfd': {}
    }
    my_util = Util()
    NSD_PATH = dir_project+'/NSD'
    VNFD_PATH = dir_project+'/VNFD'

    #import network service description
    #in root directory file name nsd.json / nsd.yaml
    for nsd_filename in glob.glob(os.path.join(NSD_PATH, '*.json')):
        print nsd_filename
        nsd_object = my_util.loadjsonfile(nsd_filename)
        project['nsd'][nsd_object['nsdIdentifier']] = nsd_object

    # import vnf descriptions
    # each file in root_path/VFND/*.json
    for vnfd_filename in glob.glob(os.path.join(VNFD_PATH, '*.json')):
        log.debug(vnfd_filename)
        vnfd_object = my_util.loadjsonfile(vnfd_filename)
        project['vnfd'][vnfd_object['vnfdId']] = vnfd_object

    #log.debug('\n' + json.dumps(project))
    return project


if __name__ == '__main__':

    test = Util()
    test_t3d = T3DUtil()

    #yaml_object = yaml.load(yaml_string)
    #log.debug(yaml_string)
    #json_object = test.yaml2json(yaml_object)
    #log.debug(json_object)
    try:
        #importProject('../../sf_dev/examples/my_example/JSON', 'json')
        project = importproject('/Users/francesco/Workspace/sf_t3d/sf_dev/examples/my_example/JSON', 'json')
        topology = test_t3d.build_graph_from_project(project)
        test.writejsonfile('/Users/francesco/Workspace/sf_t3d/sf_dev/examples/my_example/JSON/t3d.json', topology)

        # json_object_from_file = test.loadjsonfile('../../sf_dev/examples/my_example/JSON/nsd.json')
        # test.writeyamlfile('../../sf_dev/examples/my_example/YAML/nsd.yaml', json_object_from_file)
        # json_object_from_file = test.loadjsonfile('../../sf_dev/examples/my_example/JSON/VNFD/vnf1.json')
        # test.writeyamlfile('../../sf_dev/examples/my_example/YAML/VNFD/vnf1.yaml', json_object_from_file)
        # json_object_from_file = test.loadjsonfile('../../sf_dev/examples/my_example/JSON/VNFD/vnf2.json')
        # test.writeyamlfile('../../sf_dev/examples/my_example/YAML/VNFD/vnf2.yaml', json_object_from_file)
        # json_object_from_file = test.loadjsonfile('../../sf_dev/examples/my_example/JSON/VNFD/vnf3.json')
        # test.writeyamlfile('../../sf_dev/examples/my_example/YAML/VNFD/vnf3.yaml', json_object_from_file)
        # json_object_from_file = test.loadjsonfile('../../sf_dev/examples/my_example/JSON/VLD/vl1.json')
        # test.writeyamlfile('../../sf_dev/examples/my_example/YAML/VLD/vl1.yaml', json_object_from_file)
        # json_object_from_file = test.loadjsonfile('../../sf_dev/examples/my_example/JSON/VLD/vl2.json')
        # test.writeyamlfile('../../sf_dev/examples/my_example/YAML/VLD/vl2.yaml', json_object_from_file)
        # json_object_from_file = test.loadjsonfile('../../sf_dev/examples/my_example/JSON/VLD/vl3.json')
        # test.writeyamlfile('../../sf_dev/examples/my_example/YAML/VLD/vl3.yaml', json_object_from_file)
        # json_object_from_file = test.loadjsonfile('../../sf_dev/examples/my_example/JSON/VLD/vl4.json')
        # test.writeyamlfile('../../sf_dev/examples/my_example/YAML/VLD/vl4.yaml', json_object_from_file)

        #log.debug(json_object_from_file)
        #json_object_from_file = test.loadjsonfile('../../sf_dev/examples/nsd_oimsc_unique/nsd.json')
        #yaml_object_from_file = test.loadyamlfile('../../sf_dev/examples/nsd_iperf_cs/nsd.yaml')
        #log.debug(pyaml.dump(yaml_object_from_file))
        #test.writeyamlfile('../../sf_dev/examples/nsd_iperf_cs/nsd_test.yaml', yaml_object_from_file)
        #test.writejsonfile('../../sf_dev/examples/nsd_iperf_cs/nsd_test.json', test_t3d.build_graph_from_baton((json_object_from_file)))
    except IOError as e:
        #log.error('Error test')
        traceback.print_exc()