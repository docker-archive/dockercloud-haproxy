# Example of Virtual Host and Virtual Path mapping

|Virtual host|Match|Not match|
|:-----------|:----|:--------|
|`http://example.com`|`example.com`|`www.example.com`|
|`example.com`|`example.com`|`www.example.com`|
|`example.com:90`|`example.com:90`|`example.com`|
|`https://example.com`|`https://example.com`|`example.com`|
|`https://example.com:444`|`https://example.com:444`|`https://example.com`|
|`*.example.com`|`www.example.com`|`example.com`|
|`*example.com`|`www.example.com, example.com, anotherexample.com`|`www.abc.com`|
|`www.e*e.com`|`www.example.com, www.exxe.com`|`www.axxa.com`|
|`www.example.*`|`www.example.com, www.example.org`|`example.com`|
|`*/path`|`example.com/path, example.org/path?u=user`|`example.com/path/`|
|`*/path/`|`example.com/path/, example.org/path/?u=user`|`example.com/path, example.com/path/abc`|
|`*/path/*`|`example.com/path/, example.org/path/abc`|`example.com/abc/path/`|
|`*/*/path/*`|`example.com/path/, example.org/abc/path/, example.net/abc/path/123`|`example.com/path`|
|`*/*.js`|`example.com/abc.js, example.org/path/abc.js`|`example.com/abc.css`|
|`*/*.do/`|`example.com/abc.do/, example.org/path/abc.do/`|`example.com/abc.do`|
|`*/path/*.php`|`example.com/path/abc.php`|`example/abc.php, example.com/root/abc.php`|
|`*.example.com/*.jpg`|`www.example.com/abc.jpg, abc.example.com/123.jpg`|`example.com/abc.jpg`|
|`*/path, */path/`|`example.com/path, example.org/path/`||
|`example.com:90, https://example.com`|`example.com:90, https://example.com`||
|`*`|any website with HTTP||
|`https://*`|any website with HTTPS||
|`*, https://*`|any website||

**Note**:
1. The sequence of the acl rules generated based on VIRTUAL_HOST are random. In HAProxy, when an acl rule with a wide scope(e.g. *.example.com) is put before a rule with narrow scope(e.g. web.example.com), the narrow rule will never be reached. As a result, if the virtual hosts you set have overlapping scopes, you need to use `VIRTUAL_HOST_WEIGHT` to manually set the order of acl rules, namely, giving the narrow virtual host a higher weight than the wide one.
2. Every service that has the same VIRTUAL_HOST environment variable setting will be considered and merged into one single service. It may be useful for some testing scenario.

