/* jshint esversion: 6 */

const path = require("path");

const externals = ['@jupyter-widgets/base'];

const rules = [
    {
        test: /\.css$/,
        use: ['style-loader',
              {
                  loader: "css-loader",
                  options: {
                      modules: true
                  }
              }]
    }
];

module.exports = [
    {
        entry: "./index.js",
        output: {
            filename: "index.js",
            path: path.resolve(__dirname, "..", "lovett", "js"),
            libraryTarget: "amd"
        },
        resolve: {
            extensions: [".js"],
            modules: [
                "node_modules",
                path.resolve(__dirname, "..", "..", "annotald2")
            ]
        },
        module: {
            rules: rules
        },
        externals: externals,
        mode: "none"
    },
    {
        entry: "./extension.js",
        output: {
            filename: "extension.js",
            path: path.resolve(__dirname, "..", "lovett", "js"),
            libraryTarget: "amd"
        },
        mode: "none"
    }
];

// Local Variables:
// js2-include-node-externs: t
// End:
