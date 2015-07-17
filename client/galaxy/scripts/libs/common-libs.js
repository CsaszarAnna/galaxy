// common js libraries
var jquery = require( 'jquery' );
window.jQuery = window.$ = jquery;
require( './jquery/jquery.migrate' );

var _ = require( './underscore' );
window._ = _;
var Backbone = require( './backbone/backbone' );
window.Backbone = Backbone;
var Handlebars = require( './handlebars.runtime' );
window.Handlebars = Handlebars;

require( './bootstrap' );
require( './jquery/select2' );
require( '../galaxy.base' );

exports.jquery = jquery;
exports._ = _;
exports.Backbone = Backbone;
exports.Handlebars = Handlebars;
