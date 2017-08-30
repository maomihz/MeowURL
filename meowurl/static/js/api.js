"use strict";

window.Meow = (function ($) {
    var mod = {};

    var captcha_handler = null;

    // captcha = function (cap_data, callback(suc, [msg])) { }
    mod.captcha = function (arg) {
        if (arg === undefined) {
            return captcha_handler;
        } else {
            captcha_handler = arg;
        }
    };

    function req(method) {
        return function (url, arg, cb) {
            $.ajax({
                type: method,
                url: url,
                data: arg,
                dataType: "json",

                success: function (dat) {
                    // console.log(dat);
                    if (!dat.suc && dat.cap) {
                        // need captcha
                        mod.captcha()(dat.cap, function (suc, ans, msg) {
                            if (suc) {
                                // redo the request
                                req(method)(url, $.extend(arg, { capans: JSON.stringify(ans) }), cb)
                            } else
                                cb(false, msg);
                        });
                    } else cb(dat.suc, dat.res);
                },

                error: function () {
                    cb(false, "network error");
                }
            });
        };
    };

    mod.get = req("GET");
    mod.post = req("POST");

    mod.css = function (path) {
        $("<link>")
			.attr({
				rel: "stylesheet",
				href: "/static/" + path
			})
			.appendTo("head");
    };

    return mod;
})(jQuery);
