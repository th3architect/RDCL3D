if (typeof dreamer === 'undefined') {
    var dreamer = {};
}
var level = {}

dreamer.OshiController = (function(global) {
    'use strict';

    var DEBUG = true;

    OshiController.prototype.constructor = OshiController;

    /**
     * Constructor
     */
    function OshiController() {


    }


    OshiController.prototype.addNode = function(graph_editor, node, success, error) {
        log('addNode');
        var data_to_send = {
                'group_id': node.info.group[0],
                'element_id': node.id,
                'element_type': node.info.type,
                'element_desc_id': node.info.desc_id,
                'x': node.x,
                'y': node.y
         };
        new dreamer.GraphRequests().addNode(data_to_send, null, function() {
            if (success)
                success();
        },error);
    };

    OshiController.prototype.addLink = function(graph_editor, link, success, error) {
        log('addLink');
        var data_to_send = {
            'desc_id': link.desc_id,
            'source': link.source.id,
            'source_type': link.source.info.type,
            'target': link.target.id,
            'target_type': link.target.info.type,
            'view': link.view,
            'group': link.group
        };
        new dreamer.GraphRequests().addLink(data_to_send, null, function() {
            graph_editor._deselectAllNodes();
            if (typeof old_link !== 'undefined' && old_link.length > 0 && old_link[0].index !== 'undefined') {
                graph_editor.parent.removeLink.call(graph_editor, old_link[0].index);
            }
            if (success) {
                success();
            }
        },error);
    };

    OshiController.prototype.removeNode = function(graph_editor, node, success, error) {
        log('removeNode');
        var data_to_send = {
            'group_id': node.info.group[0],
            'element_id': node.id,
            'element_type': node.info.type,
            'element_desc_id': node.info.desc_id,
            };
        new dreamer.GraphRequests().removeNode(data_to_send, null, function() {
            if (success) {
                success();
            }
        },error);
    };

    OshiController.prototype.removeLink = function(graph_editor, link, success, error) {
        log('removeLink');

        link.desc_id = getUrlParameter('id');
        var data_to_send = {
            'desc_id': link.desc_id,
            'source': link.source.id,
            'source_type': link.source.info.type,
            'target': link.target.id,
            'target_type': link.target.info.type,
            'view': link.view,
            'group': link.group
        };
        new dreamer.GraphRequests().removeLink(data_to_send, function() {
            if (success) {
                success();
            }
        },error);
    };

    /**
     * Log utility
     */
    function log(text) {
        if (DEBUG)
            console.log("::OshiController::", text);
    }

    return OshiController;
}(this));

if (typeof module === 'object') {
    module.exports = dreamer.OshiController;
}