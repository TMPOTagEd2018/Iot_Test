const merge = require("webpack-merge");
const common = require("./webpack.common");
const webpack = require("webpack");
const join = require("path").join;

const CompressionPlugin = require("compression-webpack-plugin");
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
const HappyPack = require("happypack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = merge(common, {
    plugins: [
        new MiniCssExtractPlugin({
            filename: "[name].css",
            chunkFilename: "[id].css"
        }),
        new webpack.DefinePlugin({
            "process.env.NODE_ENV": JSON.stringify("production")
        }),
        // Minify JavaScript
        new UglifyJsPlugin({
            sourceMap: false,
            parallel: true,
            uglifyOptions: {
                ecma: 8
            }
        }),
        // gzip!!
        new CompressionPlugin({
            asset: "[path].gz[query]",
            algorithm: "gzip",
            test: /\.js$|\.css$/,
            threshold: 10240,
            minRatio: 0.8
        })
    ],
    mode: "production",
    module: {
        rules: [
            {
                test: /\.scss$/,
                loaders: [
                    MiniCssExtractPlugin.loader,
                    "css-loader",
                    "resolve-url-loader",
                    "sass-loader"
                ]
            },
        ]
    }
});
