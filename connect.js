// Connect - static directory
const router = require('../../nodeclient/router');
var mountFolder = function (connect, dir) {
    return connect.static(require('path').resolve(dir));
};

module.exports = {
    livereload: {
        options: {
            port: 5001,
            base: 'public',
            open: true,
            hostname: '0.0.0.0',
            middleware: function (connect, options) {
                var middlewares = [];

                middlewares = middlewares.concat(router.init());

                middlewares = middlewares.concat(require('connect-modrewrite')(['^[^\\.]*$ /index.html [L]']));

                if (!Array.isArray(options.base)) {
                    options.base = [options.base];
                }

                var directory = options.directory || options.base[options.base.length - 1];
                options.base.forEach(function (base) {
                    // Serve static files.
                    middlewares.push(connect.static(base));
                });

                // Make directory browse-able.
                middlewares.push(connect.directory(directory));

                return middlewares;
            }
        }
    },
    // livereload: {
    //     options: {
    //         port: 9000,
    //         open: true,
    //         hostname: 'sha1326003374f',
    //         middleware: function (connect, options, middlewares) {

    //             middlewares = middlewares.concat(router.init());
    //             console.log(middlewares);
    //             return [
    //                 require('connect-modrewrite')(['^[^\\.]*$ /index.html [L]']),
    //                 connect.static(require('path').resolve('public'))
    //             ];

    //         }
    //     }
    // },
    test: {
        options: {
            port: 9002,
            base: ['.tmp', '.']
        }
    },
    docs: {
        options: {
            useAvailablePort: true,
            keepalive: true,
            open: true,
            middleware: function (connect) {
                return [mountFolder(connect, '.'), mountFolder(connect, '.tmp'), mountFolder(connect, 'docs')];
            }
        }
    },
    production: {
        options: {
            keepalive: true,
            port: 8000,
            middleware: function (connect, options) {
                return [
                    // rewrite requirejs to the compiled version
                    function (req, res, next) {
                        if (req.url === 'public/bower_components/requirejs/require.js') {
                            req.url = '/dist/require.min.js';
                        }
                        next();
                    }, connect.static(options.base),

                ];
            }
        }
    }
}
