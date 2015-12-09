//global require: false

require(
    ["nbextensions/widgets/widgets/js/widget",
     "nbextensions/widgets/widgets/js/manager"],
    function(widget, manager) {
        // Define the view
        var TreesView = widget.DOMWidgetView.extend({
            initialHtml: "<div class=\"treeview-header\">" +
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
                "<div class=\"tree-display\" id=\"tree-display\"></div>",

            render: function () {
                var el = this.$el;
                var that = this;
                el.html(this.initialHtml);
                el.find(".back-btn").click(function () { that.back(); });
                el.find(".fwd-btn").click(function () { that.fwd(); });
                el.find(".treeview-maxindex").text(this.model.get("maxindex") + 1);
                this.model.on("change:index", function () { that.showTree(); });
                this.model.on("change:html", function () { that.htmlChange(); });
                this.initializeView();
            },

            initializeView: function () {
                this.showTree();

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
                var idx = this.model.get("index");
                this.$el.find(".treeview-index").text(idx + 1);
                this.send({ action: "get-tree", index: idx });
                // this.$el.find("#tree-display").html(
                //     this.model.get("trees")[this.model.get("index")]);
            },

            htmlChange: function () {
                this.$el.find("#tree-display").html(this.model.get("html"));
            }

        });

        var ResultsView = TreesView.extend({
            initialHtml: "<div class=\"treeview-header\">" +
                "<div class=\"treeview-query\">Results for query " +
                "<span class=\"treeview-query-html\"></span>" +
                "</div>" +
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
                "<div class=\"tree-display\" id=\"tree-display\"></div>",

            initializeView: function () {
                this.$el.find(".treeview-query-html").html(this.model.get("query_html"));
                this.showTree();
            }
        });

        // Register the view with the widget manager.
        manager.WidgetManager.register_widget_view('TreesView', TreesView);
        manager.WidgetManager.register_widget_view('ResultsView', ResultsView);
});
