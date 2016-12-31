if (typeof dreamer === 'undefined') {
    var dreamer = {};
}
var level = {}

dreamer.ManoGraphEditor = (function(global) {
    'use strict';

    var DEBUG = true;
    var SHIFT_BUTTON = 16;
    var IMAGE_PATH = "/static/assets/img/";
    var GUI_VERSION = "v1";


    ManoGraphEditor.prototype = new dreamer.GraphEditor();
    ManoGraphEditor.prototype.constructor = ManoGraphEditor;
    ManoGraphEditor.prototype.parent = dreamer.GraphEditor.prototype;

    /**
     * Constructor
     */
    function ManoGraphEditor(args) {

        log("Constructor");

    }


    //TODO this should be moved in graph_editor
    ManoGraphEditor.prototype.init = function(args) {
        this.parent.init.call(this, args);

        if (args.gui_properties[GUI_VERSION]!= undefined) {
            args.gui_properties = args.gui_properties[GUI_VERSION];
        }

        this.type_property = {};
        this.type_property["unrecognized"] = args.gui_properties["default"];
        this.type_property["unrecognized"]["default_node_label_color"] = args.gui_properties["default"]["label_color"];
        //this.type_property["unrecognized"]["shape"] = d3.symbolCross;

        Object.keys(args.gui_properties["nodes"]).forEach(function(key, index) {
            //console.log(key);
            this.type_property[key] = args.gui_properties["nodes"][key];
            this.type_property[key]["shape"] = this.parent.get_d3_symbol(this.type_property[key]["shape"]);
            if (this.type_property[key]["image"] != undefined ) {
                this.type_property[key]["image"] = IMAGE_PATH + this.type_property[key]["image"];
            }
            

        }, this);
        var self = this;
        d3.json("graph_data/", function(error, data) {
            //console.log(data)
            self.d3_graph.nodes = data.vertices;
            self.d3_graph.links = data.edges;
            self.d3_graph.graph_parameters = data.graph_parameters;
            //console.log(data.graph_parameters)
            self.model = data.model;
            self._setupBehaviorsOnEvents();
            self.refreshGraphParameters(self.d3_graph.graph_parameters);
            self.refresh();
            self.startForce();
            setTimeout(function() {
                self.handleForce(self.forceSimulationActive);
            }, 500);

        });
    }

    /**
     * Add a new node to the graph.
     * @param {Object} Required. An object that specifies tha data of the new node.
     * @returns {boolean}
     */
    ManoGraphEditor.prototype.addNode = function(node, success, error) {
        var self = this;
        var current_layer = self.getCurrentView()
        var node_type = node.info.type;
        if(self.model.layer[current_layer] && self.model.layer[current_layer].nodes[node_type]  && self.model.layer[current_layer].nodes[node_type].addable ){
            if(self.model.layer[current_layer].nodes[node_type].addable.callback){
                var c= self.model.callback[self.model.layer[current_layer].nodes[node_type].addable.callback].class;
                var controller = new dreamer[c]();
                controller[self.model.layer[current_layer].nodes[node_type].addable.callback](self, node, function(){
                    self.parent.addNode.call(self, node);
                    if(success)
                        success();
                }, error);
            }else{
                self.parent.addNode.call(self, node);
            }
        }
    };



    /**
     * Update the data properties of the node
     * @param {Object} Required. An object that specifies tha data of the node.
     * @returns {boolean}
     */
    ManoGraphEditor.prototype.updateDataNode = function(args) {
        this.parent.updateDataNode.call(this, args);
    };

    /**
     * Remove a node from graph and related links.
     * @param {String} Required. Id of node to remove.
     * @returns {boolean}
     */
    ManoGraphEditor.prototype.removeNode = function(node, success, error) {
        var self = this;
        var current_layer = self.getCurrentView();
        var node_type = node.info.type;
        if(self.model.layer[current_layer] && self.model.layer[current_layer].nodes[node_type]  && self.model.layer[current_layer].nodes[node_type].removable ){
                console.log(self.model.layer[current_layer].nodes[node_type].removable.callback)
            if(self.model.layer[current_layer].nodes[node_type].removable.callback){
                var c= self.model.callback[self.model.layer[current_layer].nodes[node_type].removable.callback].class;
                var controller = new dreamer[c]();
                controller[self.model.layer[current_layer].nodes[node_type].removable.callback](self, node, function(){
                    self.parent.removeNode.call(self, node);
                    if(success)
                        success();
                }, error);
            }else{
                self.parent.removeNode.call(self, node);
            }
        } else {
            alert("You can't remove a " + node.info.type );
        }
    };

    /**
     * Add a new link to graph.
     * @param {Object} Required. An object that specifies tha data of the new Link.
     * @returns {boolean}
     */
    ManoGraphEditor.prototype.addLink = function(s, d, success, error) {
        var self = this;
        var source_id = s.id;
        var target_id = d.id;
        var source_type = s.info.type;
        var destination_type = d.info.type;
        var link = {
            source: source_id,
            target: target_id,
            view: this.filter_parameters.link.view[0],
            group: this.filter_parameters.link.group,
        };
        var current_layer = self.getCurrentView()
        if(self.model.layer[current_layer].allowed_edges && self.model.layer[current_layer].allowed_edges[source_type] && self.model.layer[current_layer].allowed_edges[source_type].destination[destination_type]){
            if(self.model.layer[current_layer].allowed_edges[source_type].destination[destination_type].callback){
                var callback = self.model.layer[current_layer].allowed_edges[source_type].destination[destination_type].callback;
                var c = self.model.callback[callback].class;
                var controller = new dreamer[c]();
                controller[callback](self, s, d, function(){
                    self._deselectAllNodes();
                    self.parent.addLink.call(self, link);
                    if(success)
                        success();
                }, error);
            }else{
                self._deselectAllNodes();
                self.parent.addLink.call(self, link);
            }

        } else {
            alert("You can't link a " + source_type + " with a " + destination_type);
        }
    };

    /**
     * Remove a link from graph.
     * @param {String} Required. The identifier of link to remove.
     * @returns {boolean}
     */
    ManoGraphEditor.prototype.removeLink = function(link, success, error) {
        var self = this;
        var s = link.source;
        var d = link.target;
        var source_type = s.info.type;
        var destination_type = d.info.type;
        var current_layer = self.getCurrentView()
        if(self.model.layer[current_layer].allowed_edges && self.model.layer[current_layer].allowed_edges[source_type] && self.model.layer[current_layer].allowed_edges[source_type].destination[destination_type]
            && self.model.layer[current_layer].allowed_edges[source_type].destination[destination_type].removable
        ){
            if(self.model.layer[current_layer].allowed_edges[source_type].destination[destination_type].removable.callback){
                var callback = self.model.layer[current_layer].allowed_edges[source_type].destination[destination_type].removable.callback;
                var c = self.model.callback[callback].class;
                var controller = new dreamer[c]();
                controller[callback](self, link, function(){
                    self._deselectAllNodes();
                    self._deselectAllLinks();
                    self.parent.removeLink.call(self, link.index);
                    if(success)
                        success();
                }, error);
            }else{
                self._deselectAllNodes();
                self._deselectAllLinks();
                self.parent.removeLink.call(self, link.index);
                if(success)
                    success();
            }

        } else {
            alert("You can't delete the link" );
        }


    };


    ManoGraphEditor.prototype.savePositions = function(data) {
        var vertices = {}
        this.node.each(function(d) {
            vertices[d.id] = {}
            vertices[d.id]['x'] = d.x;
            vertices[d.id]['y'] = d.y;
        });
        new dreamer.GraphRequests().savePositions({
            'vertices': vertices
        });

    }

    /**
     *  Internal functions
     */

    /**
     *
     *
     */
    ManoGraphEditor.prototype._setupBehaviorsOnEvents = function() {
        log("_setupBehaviorsOnEvents");
        var self = this;
        var contextmenuNodesAction= [{
                    title: 'Show graph',
                    action: function(elm, c_node, i) {
                       if (c_node.info.type != undefined) {
                        var current_layer_nodes = Object.keys(self.model.layer[self.getCurrentView()].nodes);
                        if(current_layer_nodes.indexOf(c_node.info.type) >= 0 ){
                            if(self.model.layer[self.getCurrentView()].nodes[c_node.info.type].expands){
                                var new_layer = self.model.layer[self.getCurrentView()].nodes[c_node.info.type].expands;
                                self.handleFiltersParams({
                                node: {
                                    type: Object.keys(self.model.layer[new_layer].nodes),
                                    group: [c_node.id]
                                },
                                link: {
                                    group: [c_node.id],
                                    view: [c_node.info.type ]
                                }
                            });

                            }
                        }
                    }
                    }
                }, {
                    title: 'Edit',
                    action: function(elm, d, i) {
                        if (d.info.type != undefined) {
                            window.location.href = '/projects/' + self.project_id + '/descriptors/' + graph_editor.getCurrentView() + 'd/' + graph_editor.getCurrentGroup();
                        }
                    }

                }, {
                    title: 'Delete',
                    action: function(elm, d, i) {
                        self.removeNode(d);
                    }

                }];
        if(self.model && self.model.action && self.model.action.node ){
            console.log(this.model)
            for (var i in self.model.action.node){
                var action = self.model.action.node[i]
                contextmenuNodesAction.push({
                title: action.title,
                action: function(elm, d, i) {
                        var callback = action.callback;
                        var c = self.model.callback[callback].class;
                        var controller = new dreamer[c]();
                        var args = {elm: elm,
                                    d: d,
                                    i: i}

                        controller[callback](self, args);
                 }
                });
            }
        }
        var contextmenuLinksAction = [{
                    title: 'Delete Link',
                    action: function(elm, link, i) {
                        self.removeLink(link);
                    }

                }];
        if(self.model && self.model.action && self.model.action.link ){
            for (var i in self.model.action.link){
                var action = self.model.action.link[i]
                contextmenuLinksAction.push({
                title: action.title,
                action: function(elm, link, i) {
                        var callback = action.callback;
                        var c = self.model.callback[callback].class;
                        var controller = new dreamer[c]();
                        var args = {elm: elm,
                                    link: link,
                                    i: i}

                        controller[callback](self, args);
                 }
                });
            }
        }

        this.behavioursOnEvents = {
            'nodes': {
                'click': function(d) {

                    d3.event.preventDefault();

                    if (self.lastKeyDown == SHIFT_BUTTON && self._selected_node != undefined) {
                        self.addLink(self._selected_node, d);
                    } else {
                        self._selectNodeExclusive(this, d);
                    }

                },
                'mouseover': function(d) {
                    self.link.style('stroke-width', function(l) {
                        if (d === l.source || d === l.target)
                            return 4;
                        else
                            return 2;
                    });
                },
                'mouseout': function(d) {
                    self.link.style('stroke-width', 2);
                },
                'dblclick': function(c_node) {
                     d3.event.preventDefault();
                    log('dblclick ');
                    if (c_node.info.type != undefined) {
                        var current_layer_nodes = Object.keys(self.model.layer[self.getCurrentView()].nodes);
                        if(current_layer_nodes.indexOf(c_node.info.type) >= 0 ){
                            if(self.model.layer[self.getCurrentView()].nodes[c_node.info.type].expands){
                                var new_layer = self.model.layer[self.getCurrentView()].nodes[c_node.info.type].expands;
                                self.handleFiltersParams({
                                node: {
                                    type: Object.keys(self.model.layer[new_layer].nodes),
                                    group: [c_node.id]
                                },
                                link: {
                                    group: [c_node.id],
                                    view: [c_node.info.type ]
                                }
                            });

                            }
                        }
                    }

                },
                'contextmenu': d3.contextMenu(contextmenuNodesAction)
            },
            'links': {
                'click': function(d) {
                    self._selectLinkExclusive(this, d);

                },
                'dblclick': function(event) {

                },
                'mouseover': function(d) {
                    d3.select(this).style('stroke-width', 4);
                },
                'mouseout': function(d) {
                    if (d != self._selected_link)
                        d3.select(this).style('stroke-width', 2);
                },
                'contextmenu': d3.contextMenu(contextmenuLinksAction)
            }
        };
    };

    ManoGraphEditor.prototype.exploreLayer = function(args) {

    };

    ManoGraphEditor.prototype.getTypeProperty = function() {
        return this.type_property;
    };

    ManoGraphEditor.prototype.getCurrentGroup = function() {
        return this.filter_parameters.node.group[0];

    }
    ManoGraphEditor.prototype.getCurrentView = function() {
        return this.filter_parameters.link.view[0];

    }
    /**
     * Log utility
     */
    function log(text) {
        if (DEBUG)
            console.log("::ModelGraphEditor::", text);
    }



    return ManoGraphEditor;


}(this));

if (typeof module === 'object') {
    module.exports = dreamer.ManoGraphEditor;
}