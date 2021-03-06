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

import string
import copy
import networkx as nx
from declaration import *
from createJson import *

def remove_tab(line):
    if string.find(line,'\t') != -1:
        print 'ok'
        line=line[string.find(line,'\t')+1:]
        line = remove_tab(line)
    return line

def generateTopology(element, connection, nx_topology):
    # nx_topology.add_node(int(node_id_value), city = node_name_value, country = node_country_value, type_node = 'core' )
    # add_edge(src, dst, flow_id, {'size':flow_dict['out']['size'], 'path':[]})

    for e in range(0, len(element)):
        nx_topology.add_node(element[e]['name'], element=element[e]['element'], config=element[e]['config'],
                             flowcode='', processing='', portcount='')

    for c in range(0, len(connection)):
        nx_topology.add_edge(connection[c]['source'], connection[c]['dest'], 'port_config',
                             {'port_input': connection[c]['port-input'], 'port_output': connection[c]['port-output']})


def generateJsont3d(element, connection):
    json_data = nx_2_t3d_json(element, connection, 'out.t3d')
    return json_data


def parserView(file_click, nx_topology):

    words = []
    compound_element_content=[]
    element = {}
    connection = {}
    line2 = ''
    concatenate = False

    text = "".join([s for s in file_click.splitlines(True) if s.strip("\r\n")])

    for line in text.splitlines():
        if line[0] != "/":

            if string.find(line, '//') != -1:  # elimina i commenti dalla riga
                line = line[0:string.find(line, '//') - 1]

            if string.find(line, '[') != -1:  # questo blocco modifica l'intera linea per gestire la lettura
                index = string.find(line, '[')  # delle porte di uscita dell'elemento che possono essere scritte
                if line[index - 1] == ' ' and line[index - 2].islower():  # sia come [num]port che [num] port
                    line = line[0:index - 1] + '' + line[index:]

            if string.find(line, '{') != -1:

                line2 = line
                concatenate = True
                continue
            elif concatenate:
                line = line2 + ' ' + line
                start = string.find(line, '{')
                stop = string.find(line, '}')
                concatenate = False
                line2 = ''

                line , compound_element_content = compound_element_view(line,compound_element_content)
                #compound_element_content contiene ora il contenuto del compound element
            explicit_elment_decl(line, element)
            implicit_element_decl(line, element)
            load_list(line, words)

    rename_element_list(element, words)

    connection_decl(words, connection, element)

    '''#print di controllo per compound_element_content
    print '!!!!!!!!!!!!!!!!!!!!'
    #print comp_elem_content
    print map(lambda x: x.encode('ascii'), compound_element_content)
    print '********************'
    '''

    print '\n'
    print element
    print'\n \n \n \n'
    print words
    # print connection
    words[:] = []

    # generateTopology(element, connection, nx_topology)			#genera la topologia per nx
    json_data = generateJsont3d(element, connection)  # genera elemento Json

    return json_data
