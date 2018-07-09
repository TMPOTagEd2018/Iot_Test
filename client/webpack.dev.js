const path = require("path");
const merge = require("webpack-merge");
const common = require("./webpack.common");
const webpack = require("webpack");
const happypack = require("happypack");
const CompressionPlugin = require("compression-webpack-plugin");
const WriteFilePlugin = require("write-file-webpack-plugin");
const HardSourceWebpackPlugin = require("hard-source-webpack-plugin");

module.exports = merge(common, {
    devtool: "eval-source-map",
    mode: "development",
    devServer: {
        noInfo: true
    },
    // entry: ["webpack-hot-middleware/client"],
    plugins: [
        new HardSourceWebpackPlugin(),

        new webpack.optimize.OccurrenceOrderPlugin(false),
        new webpack.NoEmitOnErrorsPlugin(),
        new webpack.NamedModulesPlugin(),
        new webpack.DefinePlugin({
            "process.env.NODE_ENV": JSON.stringify("development")
        }),
        new WriteFilePlugin(), // force webpack-dev-server to use filesystem instead of mem system
    ],
    module:
        {
            rules: [
                {
                    test: /\.scss$/,
                    loaders: [
                        "vue-style-loader",
                        "cache-loader",
                        "css-loader",
                        "resolve-url-loader",
                        "sass-loader"
                    ]
                },
            ]
        }
});
