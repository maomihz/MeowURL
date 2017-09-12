"use strict";

window.Meow = (function ($) {
    var mod = {};
<<<<<<< HEAD

    var captcha_handler = null;

=======
    
    var captcha_handler = null;
    
>>>>>>> 90e9d194cc8a88f67ba76be8a32fd184fd5b662c
    // captcha = function (cap_data, callback(suc, [msg])) { }
    mod.captcha = function (arg) {
        if (arg === undefined) {
            return captcha_handler;
        } else {
            captcha_handler = arg;
        }
    };
<<<<<<< HEAD

=======
    
>>>>>>> 90e9d194cc8a88f67ba76be8a32fd184fd5b662c
    function req(method) {
        return function (url, arg, cb) {
            $.ajax({
                type: method,
                url: url,
                data: arg,
                dataType: "json",
<<<<<<< HEAD

=======
                
>>>>>>> 90e9d194cc8a88f67ba76be8a32fd184fd5b662c
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
<<<<<<< HEAD

=======
                
>>>>>>> 90e9d194cc8a88f67ba76be8a32fd184fd5b662c
                error: function () {
                    cb(false, "network error");
                }
            });
        };
    };
<<<<<<< HEAD

    mod.get = req("GET");
    mod.post = req("POST");

=======
    
    mod.get = req("GET");
    mod.post = req("POST");
    
>>>>>>> 90e9d194cc8a88f67ba76be8a32fd184fd5b662c
    mod.css = function (path) {
        $("<link>")
			.attr({
				rel: "stylesheet",
				href: "/static/" + path
			})
			.appendTo("head");
    };
<<<<<<< HEAD

=======
    
>>>>>>> 90e9d194cc8a88f67ba76be8a32fd184fd5b662c
    return mod;
})(jQuery);
