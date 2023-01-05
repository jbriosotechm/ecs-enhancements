// // Create token
const myArgs = process.argv.slice(2);
var CryptoJS = require("crypto-js");

// Create token
var key_id = "7940d5c76b8082ee68601b43035b3362";
var key = "a8m2symkvl1sz1sd6kx8bk54vjigtijadgddnpfztcp7vuelopqqfsp";
var operator_name = "globegomo";
var epoch = new Date().getTime() / 1000 | 0;
var removeIllegalCharacters = function(input) {
    return input
        .replace(/=/g, '')
        .replace(/\+/g, '-')
        .replace(/\//g, '_');
};
var base64object = function(input) {
    var inputWords = CryptoJS.enc.Utf8.parse(JSON.stringify(input));
    var base64 = CryptoJS.enc.Base64.stringify(inputWords);
    var output = removeIllegalCharacters(base64);
    return output;
};

var url = myArgs[0];
var path1 = url.substring(url.indexOf(":", 0) + 3)
var path = path1.substring(path1.indexOf("/"));
var header = { 'alg': 'HS256', 'typ': 'JWT' };
var payload = { 'epoch': epoch,
                'operator_name': operator_name,
                'path': path,
                'version': "1",
                'type': 1,
                'key_id': key_id
            };
var unsignedToken = base64object(header) + "." + base64object(payload);
var signatureHash = CryptoJS.HmacSHA256(unsignedToken, key);
var signature = CryptoJS.enc.Base64.stringify(signatureHash);
var token = unsignedToken + '.' + signature;
console.log("Bearer " + removeIllegalCharacters(token));