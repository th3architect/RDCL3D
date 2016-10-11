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

    def delete_descriptor(self,type_descriptor, descriptor_id ):
        try:
            print descriptor_id, type_descriptor
            current_data = json.loads(self.data_project)
            del (current_data[type_descriptor][descriptor_id])
            self.data_project = current_data#jsonfield.JSONField(json.dumps(current_data))
            self.update()
            result = True
        except Exception as e:
            print 'exception',e
            result = False
        return result

    def create_descriptor(self, type_descriptor, text, data_type):

        try:
            print type_descriptor, data_type
            current_data = json.loads(self.data_project)
            if data_type == 'json':
                new_descriptor = json.loads(text)
            else:
                utility = Util()
                yaml_object = yaml.load(text)
                new_descriptor = json.loads(utility.yaml2json(yaml_object))
            new_descriptor_id = new_descriptor['id'] if type_descriptor != "nsd" else new_descriptor['name']
            current_data[type_descriptor][new_descriptor_id] = new_descriptor
            self.data_project = current_data
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
