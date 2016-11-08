from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import jsonfield
from StringIO import StringIO
import zipfile
import json
import yaml
from lib.emparser.util import Util
# Create your models here.


class Project(models.Model):

    owner = models.ForeignKey('sf_user.CustomUser', db_column='owner')
    name = models.CharField(max_length=20)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    info = models.TextField(default='No info')
    data_project = jsonfield.JSONField(default={'nsd': {}, 'vld': {}, 'vnfd': {}, 'vnffgd': {}})
    validated = models.BooleanField(default=False)

    def get_dataproject(self):
        current_data = json.loads(self.data_project)
        return  current_data

    def get_overview_data(self):
        result = {
            'owner': self.owner,
            'name': self.name,
            'updated_date': self.updated_date,
            'info': self.info,
            'validated': self.validated
        }

        return result

    def set_data_project(self, new_data, validated):
        self.data_project = new_data
        self.set_validated(validated)
        self.update()

    def update(self):
        self.updated_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class EtsiManoProject(Project):


    def get_descriptors(self, type_descriptor):
        try:
            current_data = json.loads(self.data_project)
            result = current_data[type_descriptor]
        except Exception as e:
            result = {}
        return result

    def get_descriptor(self, descriptor_id, type_descriptor):

        try:
            current_data = json.loads(self.data_project)
            result = current_data[type_descriptor][descriptor_id]
        except:
            result = {}

        return result

    def delete_descriptor(self,type_descriptor, descriptor_id):
        try:
            print descriptor_id, type_descriptor
            current_data = json.loads(self.data_project)
            del (current_data[type_descriptor][descriptor_id])
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception',e
            result = False
        return result

    def edit_descriptor(self, type_descriptor, descriptor_id, new_data, data_type):
        try:
            utility = Util()
            print descriptor_id, type_descriptor
            current_data = json.loads(self.data_project)
            if data_type == 'json':
                new_descriptor = json.loads(new_data)
            else:
                yaml_object = yaml.load(new_data)
                new_descriptor = json.loads(utility.yaml2json(yaml_object))
            utility.validate_json_schema(type_descriptor, new_descriptor)
            current_data[type_descriptor][descriptor_id] = new_descriptor
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def create_descriptor(self, type_descriptor, new_data, data_type):
        try:
            utility = Util()
            print type_descriptor, data_type
            current_data = json.loads(self.data_project)
            if data_type == 'json':
                new_descriptor = json.loads(new_data)
            else:
                utility = Util()
                yaml_object = yaml.load(new_data)
                new_descriptor = json.loads(utility.yaml2json(yaml_object))
            validate = utility.validate_json_schema(type_descriptor, new_descriptor)
            new_descriptor_id = new_descriptor['id'] if type_descriptor != "nsd" else new_descriptor['name']
            if not type_descriptor in current_data:
                current_data[type_descriptor] = {}
            current_data[type_descriptor][new_descriptor_id] = new_descriptor
            self.data_project = current_data
            self.validated = validate
            self.update()
            result = True
        except Exception as e:
            print 'exception',e
            result = False
        return result


    def set_validated(self, value):
        self.validated = True if value is not None and value == True else False

    def get_zip_archive(self):
        in_memory = StringIO()
        try:
            current_data = json.loads(self.data_project)
            zip = zipfile.ZipFile(in_memory, "w", zipfile.ZIP_DEFLATED)
            for desc_type in current_data:
                for current_desc in current_data[desc_type]:
                    zip.writestr(current_desc+'.json', json.dumps(current_data[desc_type][current_desc]))

            zip.close()
        except Exception as e:
            print e


        #zip.writestr("file1.txt", "some text contents")
        #zip.writestr("file2", "csv,data,here")

        # fix for Linux zip files read in Windows
        #for file in zip.filelist:
        #    print file.filename

        #    file.create_system = 0
        #zip.filelist

        in_memory.flush()
        return in_memory

    def update(self):
        self.updated_date = timezone.now()
        self.save()

    def get_overview_data(self):
        #print self.owner,self.name,self.updated_date, self.info
        #print type(self.data_project)
        current_data = json.loads(self.data_project)
        #print 'nsd' in current_data, len(current_data['nsd'].keys())
        result = {
            'owner': self.owner,
            'name': self.name,
            'updated_date': self.updated_date,
            'info': self.info,
            'nsd': len(current_data['nsd'].keys()) if 'nsd' in current_data else 0,
            'vnffgd': len(current_data['vnffgd'].keys()) if 'vnffgd' in current_data else 0,
            'vld': len(current_data['vld'].keys()) if 'vld' in current_data else 0,
            'vnfd': len(current_data['vnfd'].keys()) if 'vnfd' in current_data else 0,
            'validated': self.validated
        }

        return result

    def __str__(self):
        return self.name

    def edit_graph_positions(self, positions):
        print positions
        try:
            current_data = json.loads(self.data_project)
            if 'positions' not in current_data :
                current_data['positions'] = {}
            if 'vertices' not in current_data['positions'] :
                current_data['positions']['vertices'] = {}
            if 'vertices' in positions :
                current_data['positions']['vertices'].update(positions['vertices'])
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception',e
            result = False
        return result

    # NS operations: add/remove VL
    def add_ns_vl(self, ns_id, vl_id):
        try:
            current_data = json.loads(self.data_project)
            utility = Util()
            ns = utility.get_descriptor_template('nsd')
            vl_descriptor = ns['virtualLinkDesc'][0]
            vl_descriptor['virtualLinkDescId'] = vl_id
            current_data['nsd'][ns_id]['virtualLinkDesc'].append(vl_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception',e
            result = False
        return result

    def remove_ns_vl(self, ns_id, vl_id):
        try:
            current_data = json.loads(self.data_project)
            vl_descriptor = next((x for x in current_data['nsd'][ns_id]['virtualLinkDesc'] if x['virtualLinkDescId'] == vl_id),None)
            if vl_descriptor is not None:
                current_data['nsd'][ns_id]['virtualLinkDesc'].remove(vl_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception',e
            result = False
        return result

    def edit_ns_vl(self, ns_id, vl_id, vl_descriptor):
        try:
            current_data = json.loads(self.data_project)
            self.remove_ns_vl(ns_id, vl_id)
            current_data['nsd'][ns_id]['virtualLinkDesc'].append(vl_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception',e
            result = False
        return result

    # NS operations: add/remove SAP
    def add_ns_sap(self, ns_id, sap_id):
        try:
            current_data = json.loads(self.data_project)
            utility = Util()
            ns = utility.get_descriptor_template('nsd')
            sap_descriptor = ns['sapd'][0]
            sap_descriptor['cpdId'] = sap_id
            current_data['nsd'][ns_id]['sapd'].append(sap_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def remove_ns_sap(self, ns_id, sap_id):
        try:
            current_data = json.loads(self.data_project)
            sap_descriptor = next((x for x in current_data['nsd'][ns_id]['sapd'] if x['cpdId'] == sap_id), None)
            if sap_descriptor is not None:
                current_data['nsd'][ns_id]['sapd'].remove(sap_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def edit_ns_sap(self, ns_id, sap_id, sap_descriptor):
        try:
            current_data = json.loads(self.data_project)
            self.remove_ns_sap(ns_id, sap_id)
            current_data['nsd'][ns_id]['sapd'].append(sap_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    # NS operations: add/remove VNF
    def add_ns_vnf(self, ns_id, vnf_id):
        #Aggingi l'id a vnfProfile e aggiungi un entry in nsDf e creare il file descriptor del VNF
        try:
            current_data = json.loads(self.data_project)
            utility = Util()
            current_data['nsd'][ns_id]['vnfdId'].append(vnf_id)
            vnf_profile = utility.get_descriptor_template('nsd')['nsDf'][0]['vnfProfile'][0]
            vnf_profile['vnfdId'] = vnf_id
            current_data['nsd'][ns_id]['nsDf'][0]['vnfProfile'].append(vnf_profile)
            vnf_descriptor = utility.get_descriptor_template('vnf')
            vnf_descriptor['vnfdId'] = vnf_id
            vnf_descriptor['vdu'] = []
            vnf_descriptor['intVirtualLinkDesc'] = []
            vnf_descriptor['vnfExtCpd'] = []
            current_data['vnfd'][vnf_id] = vnf_descriptor
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result


    def remove_ns_vnf(self, ns_id, vnf_id):
        try:
            current_data = json.loads(self.data_project)
            current_data['nsd'][ns_id]['vnfdId'].remove(vnf_id)
            vnf_profile = next((x for x in current_data['nsd'][ns_id]['nsDf'][0]['vnfProfile'] if x['vnfdId'] == vnf_id), None)
            if vnf_profile is not None:
                current_data['nsd'][ns_id]['nsDf'][0]['vnfProfile'].remove(vnf_profile)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def edit_ns_vnf(self, vnf_id, vnf_descriptor):
        try:
            current_data = json.loads(self.data_project)
            current_data['vnfd'][vnf_id] = vnf_descriptor
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    #NS operations: add/remove Nested NS
    def add_ns_nsNested (self, ns_id, nested_ns_id):
        try:
            current_data = json.loads(self.data_project)
            current_data['nsd'][ns_id]['nestedNsdId'].append(nested_ns_id)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    # NS operations: link/Unlink Sap with VL
    def link_vl_sap(self, ns_id, vl_id, sap_id):
        try:
            current_data = json.loads(self.data_project)
            sap_descriptor = next((x for x in current_data['nsd'][ns_id]['sapd'] if x['cpdId'] == sap_id), None)
            sap_descriptor['nsVirtualLinkDescId'] = vl_id
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def unlink_vl_sap(self, ns_id, vl_id, sap_id):
        try:
            current_data = json.loads(self.data_project)
            sap_descriptor = next((x for x in current_data['nsd'][ns_id]['sapd'] if x['cpdId'] == sap_id), None)
            del sap_descriptor['nsVirtualLinkDescId']
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    # NS operations: link/Unlink VNF with VL
    def link_vl_vnf(self, ns_id, vl_id, vnf_id, ext_cp_id):
        try:
            utility = Util()
            current_data = json.loads(self.data_project)
            vnf_profile = next((x for x in current_data['nsd'][ns_id]['nsDf']['vnfProfile'] if x['vnfdId'] == vnf_id),None)
            virtual_link_connectivity = utility.get_descriptor_template('nsd')['nsDf']['vnfProfile'][0]['nsVirtualLinkConnectivity'][0]
            virtual_link_connectivity['cpdId'].append(ext_cp_id)
            vnf_profile["nsVirtualLinkConnectivity"].append(virtual_link_connectivity)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result


    def unlink_vl_vnf(self, ns_id, vl_id, vnf_id, ext_cp_id):
        try:
            current_data = json.loads(self.data_project)
            vnf_profile = next((x for x in current_data['nsd'][ns_id]['nsDf']['vnfProfile'] if x['vnfdId'] == vnf_id), None)
            virtual_link_connectivity = next((x for x in vnf_profile['nsVirtualLinkConnectivity'] if ext_cp_id in x['cpdId'] ), None)
            if virtual_link_connectivity is not None:
                virtual_link_connectivity['cpdId'].remove(ext_cp_id)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    #VNF operationd: add/remove VDU
    def add_vnf_vdu(self, vnf_id, vdu_id):
        try:
            current_data = json.loads(self.data_project)
            utility = Util()
            vdu_descriptor = utility.get_descriptor_template('vnf')['vdu'][0]
            vdu_descriptor['vduId'] = vdu_id
            vdu_descriptor['intCpd'] = []
            current_data['vnfd'][vnf_id]['vdu'].append(vdu_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception',e
            result = False
        return result

    def remove_vnf_vdu(self, vnf_id, vdu_id):
        try:
            current_data = json.loads(self.data_project)
            vdu_descriptor = next((x for x in current_data['vnfd'][vnf_id]['vdu'] if x['vduId'] == vdu_id), None)
            if vdu_descriptor is not None:
                current_data['vnfd'][vnf_id]['vdu'].remove(vdu_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def edit_vnf_vdu(self, vnf_id, vdu_id, vdu_descriptor):
        try:
            current_data = json.loads(self.data_project)
            self.remove_vnf_vdu(vnf_id, vdu_id)
            current_data['vnfd'][vnf_id]['vdu'].append(vdu_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    # VNF operationd: add/remove CP VDU
    def add_vnf_vducp(self, vnf_id, vdu_id, vducp_id):
        try:
            current_data = json.loads(self.data_project)
            utility = Util()
            vdu_descriptor = next((x for x in current_data['vnfd'][vnf_id]['vdu'] if x['vduId'] == vdu_id), None)
            intcp_descriptor = utility.get_descriptor_template('vnf')['vdu'][0]['intCpd'][0]
            intcp_descriptor['cpdId'] = vducp_id
            vdu_descriptor['intCpd'].append(intcp_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def remove_vnf_vducp(self, vnf_id, vdu_id, vducp_id):
        try:
            current_data = json.loads(self.data_project)
            vdu_descriptor = next((x for x in current_data['vnfd'][vnf_id]['vdu'] if x['vduId'] == vdu_id), None)
            intcp_descriptor = next((x for x in vdu_descriptor['intCpd'] if x['cpdId'] == vducp_id), None)
            vdu_descriptor['intCpd'].remove(intcp_descriptor)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    # VNF operationd: link/unlink VduCP and IntVL
    def link_vducp_intvl(self, vnf_id, vdu_id, vducp_id, intvl_id):
        try:
            current_data = json.loads(self.data_project)
            vdu_descriptor = next((x for x in current_data['vnfd'][vnf_id]['vdu'] if x['vduId'] == vdu_id), None)
            intcp_descriptor = next((x for x in vdu_descriptor['intCpd'] if x['cpdId'] == vducp_id), None)
            intcp_descriptor['intVirtualLinkDesc'] = intvl_id
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def unlink_vducp_intvl(self, vnf_id, vdu_id, vducp_id, intvl_id):
        try:
            current_data = json.loads(self.data_project)
            vdu_descriptor = next((x for x in current_data['vnfd'][vnf_id]['vdu'] if x['vduId'] == vdu_id), None)
            intcp_descriptor = next((x for x in vdu_descriptor['intCpd'] if x['cpdId'] == vducp_id), None)
            del intcp_descriptor['intVirtualLinkDesc']
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    #VNF operationd: add/remove IntVL
    def add_vnf_intvl(self, vnf_id, intvl_id):
        try:
            current_data = json.loads(self.data_project)
            utility = Util()
            intVirtualLinkDesc = utility.get_descriptor_template('vnf')['intVirtualLinkDesc'][0]
            intVirtualLinkDesc['virtualLinkDescId'] = intvl_id
            current_data['vnfd'][vnf_id]['intVirtualLinkDesc'].append(intVirtualLinkDesc)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def remove_vnf_intvl(self, vnf_id, intvl_id):
        try:
            current_data = json.loads(self.data_project)
            utility = Util()
            intVirtualLinkDesc = next((x for x in current_data['vnfd'][vnf_id]['intVirtualLinkDesc'] if x['virtualLinkDescId'] == intvl_id), None)
            current_data['vnfd'][vnf_id]['intVirtualLinkDesc'].remove(intVirtualLinkDesc)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    # VNF operationd: add/remove vnfExtCpd
    def add_vnf_vnfextcpd(self, vnf_id, vnfExtCpd_id):
        try:
            current_data = json.loads(self.data_project)
            utility = Util()
            vnfExtCpd = utility.get_descriptor_template('vnf')['vnfExtCpd'][0]
            vnfExtCpd['cpdId'] = vnfExtCpd_id
            current_data['vnfd'][vnf_id]['vnfExtCpd'].append(vnfExtCpd)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def remove_vnf_vnfextcpd(self, vnf_id, vnfExtCpd_id):
        try:
            current_data = json.loads(self.data_project)
            utility = Util()
            vnfExtCpd = next((x for x in current_data['vnfd'][vnf_id]['vnfExtCpd'] if x['cpdId'] == vnfExtCpd_id), None)
            current_data['vnfd'][vnf_id]['vnfExtCpd'].remove(vnfExtCpd)
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    # VNF operationd: link/unlink vnfextcpd and IntVL
    def link_vnfextcpd_intvl(self, vnf_id, vnfExtCpd_id, intvl_id):
        try:
            print vnf_id, vnfExtCpd_id, intvl_id
            current_data = json.loads(self.data_project)
            vnfExtCpd = next((x for x in current_data['vnfd'][vnf_id]['vnfExtCpd'] if x['cpdId'] == vnfExtCpd_id), None)
            vnfExtCpd['intVirtualLinkDesc'] = intvl_id
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result

    def unlink_vnfextcpd_intvl(self, vnf_id, vnfExtCpd_id, intvl_id):
        try:
            current_data = json.loads(self.data_project)
            vnfExtCpd = next((x for x in current_data['vnfd'][vnf_id]['vnfExtCpd'] if x['cpdId'] == vnfExtCpd_id), None)
            del vnfExtCpd['intVirtualLinkDesc']
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'exception', e
            result = False
        return result