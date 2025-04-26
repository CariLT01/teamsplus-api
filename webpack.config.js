const TerserPlugin = require('terser-webpack-plugin');
const path = require('path');

module.exports = {
    mode: 'production',
    entry: {
        'static/js/login/script': './src/client/login/script.ts',
        'static/js/register/script': './src/client/register/script.ts',
        'static/js/dashboard/script': './src/client/dashboard/script.ts',
        'static/js/home/script': './src/client/home/script.ts',
        'static/js/game_of_life/src/bundle': "./src/client/game_of_life/main.ts"
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
    optimization: {
        minimize: false,
      }
};