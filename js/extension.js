/* global __webpack_public_path__: true */
/* jshint esversion: 6 */

__webpack_public_path__ = document.querySelector('body').getAttribute('data-base-url') + 'nbextensions/lovett';

// Configure requirejs
if (window.require) {
    window.require.config({
        map: {
            "*" : {
                "lovett": "nbextensions/lovett/index",
            }
        }
    });
}

// Export the required load_ipython_extension
module.exports = {
    load_ipython_extension: function() {}
};

// Local Variables:
// js2-include-node-externs: t
// End:
