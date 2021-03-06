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

from django.conf.urls import url
from deploymenthandler import views

urlpatterns = [
    url(r'^list/', views.agents_list, name='agents_list'),
    url(r'^new/', views.new_agent, name='new_agent'),
    url(r'^(?P<agent_id>\d+)/delete$', views.delete_agent, name='delete_agent'),

]