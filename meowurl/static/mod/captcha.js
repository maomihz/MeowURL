/* captcha */

define([ "mod/util" ], function (util) {
    var mod = {};
    var $ = jQuery;
    
    Meow.css("mod/captcha.css");
    
    mod.modal = function (cap, cb, config) {
        config = $.extend({}, config);
        
        initGeetest({
            gt: cap.gt,
            challenge: cap.challenge,
            offline: cap.offline,
            
            product: "bind"
        }, function (cap_obj) {
            cap_obj.onSuccess(function () {
                var valid = cap_obj.getValidate();
                cb(true, {
                    challenge: valid.geetest_challenge,
                    validate: valid.geetest_validate,
                    seccode: valid.geetest_seccode
                });
            });
            
            cap_obj.onError(function () {
                cb(false, null, "captcha error(try later)");
            });
            
            cap_obj.onClose(function () {
                cb(false, null, "request cancelled");
            });
            
            cap_obj.onReady(function () {
                cap_obj.verify();
            });
        });
    }
    
    return mod;
});
