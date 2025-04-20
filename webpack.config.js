const path = require('path');

module.exports = {
    mode: 'production',
    entry: {
        'static/login/script': './static/login/script.ts',
        'static/register/script': './static/register/script.ts',
        'static/dashboard/script': './static/dashboard/script.ts',
        'static/home/script': './static/home/script.ts',
        'static/life/script': './static/life/script.ts'
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname),
    },
    resolve: {
        extensions: ['.ts', '.js'],
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
        ],
    },
    cache: {
        type: 'filesystem',  // Enable filesystem caching
        buildDependencies: {
          config: [__filename],  // Cache invalidates if the config file changes
        },
      },
    mode: 'production', // Set the mode to production for optimizations
};