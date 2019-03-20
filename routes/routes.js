var async = require('async');

var getHome = function(req, res) {
	res.render('home.ejs');
};

var routes = {
		get_homepage : getHome
};

module.exports = routes;
