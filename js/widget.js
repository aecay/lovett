/* global define: false */

/* jshint esversion: 6 */

const tree_view = require("tree-view.js");
const widgets = require("@jupyter-widgets/base");
const style = require("../../annotald2/python/static/index.css");

const LovettTree = widgets.DOMWidgetView.extend({
    render: function () {
        this.model.on("change:tree", tree_changed, this);
        var container = document.createElement("div");
        this.el.appendChild(container);
        var view = tree_view.Elm.TreeView.init({
            node: container,
            flags: {
                tree: this.model.get("tree"),
                snodeClass: style.snode,
                ipClass: style.ip,
                selectedClass: style.selected,
                wnodeClass: style.wnode
            }
        });

        function tree_changed() {
            view.ports.treeChanged.send(this.model.get("tree"));
        }
    }

});

module.exports = {
    LovettTree: LovettTree
};

// Local Variables:
// js2-include-node-externs: t
// End:
