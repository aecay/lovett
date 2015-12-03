//global require: false

require(
    ["nbextensions/widgets/widgets/js/widget",
     "nbextensions/widgets/widgets/js/manager"],
    function(widget, manager) {
        // Define the view
        var TreesView = widget.DOMWidgetView.extend({
            render: function () {
                var el = this.$el;
                var that = this;
                el.html("<div class=\"treeview-header\">" +
                        "<span class=\"treeview-info\">" +
                        "<span class=\"treeview-index\"></span>" +
                        "/" +
                        "<span class=\"treeview-maxindex\"></span>" +
                        "</span>" +
                        "<span class=\"treeview-buttons\">" +
                        "<button type=\"button\" class=\"back-btn\">&lt;</input>" +
                        "<button type=\"button\" class=\"fwd-btn\">&gt;</input>" +
                        "</span>" +
                        "</div>" +
                        "<div class=\"tree-display\" id=\"tree-display\"></div>");
                el.find(".back-btn").click(function () { that.back(); });
                el.find(".fwd-btn").click(function () { that.fwd(); });
                el.find(".treeview-maxindex").text(this.model.get("maxindex") + 1);
                this.model.on("change:index", function () { that.showTree(); });
                that.showTree();
            },

            back: function () {
                this.model.set("index",
                               Math.max(this.model.get("index") - 1, 0));
            },

            fwd: function () {
                this.model.set("index",
                               Math.min(this.model.get("index") + 1,
                                        this.model.get("maxindex")));
            },

            showTree: function () {
                this.$el.find(".treeview-index").text(this.model.get("index") + 1);
                this.$el.find("#tree-display").html(
                    this.model.get("trees")[this.model.get("index")]);
            }

            // TODO: should be able to use this.send(content) to send messages
            // to python.  corresponiding python function is Widget.on_msg
        });

        // Register the view with the widget manager.
        manager.WidgetManager.register_widget_view('TreesView', TreesView);
});
