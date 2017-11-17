const webpack = require('webpack');

module.exports = {
    entry: [
        "react-hot-loader/patch",
        "./front/hot.tsx"
    ],
    output: {
        filename: "app.js",
        path: __dirname + "/back/static/"
    },

    // Enable sourcemaps for debugging webpack's output.
    devtool: "eval",

    resolve: {
        // Add '.ts' and '.tsx' as resolvable extensions.
        extensions: [".ts", ".tsx", ".js", ".json"]
    },

    devServer: {
        contentBase: "./back/static",
        overlay: true,
        hot: true
    },

    module: {
        rules: [
            // All files with a '.ts' or '.tsx' extension will be handled by 'awesome-typescript-loader'.
            {
                test: /\.tsx?$/,
                use: [
                    {loader: "react-hot-loader/webpack"},
                    {loader: "awesome-typescript-loader"}
                ]
            },
            // All output '.js' files will have any sourcemaps re-processed by 'source-map-loader'.
            {enforce: "pre", test: /\.js$/, loader: "source-map-loader"},
            {test: /\.styl$/, loaders: ['style-loader', 'css-loader', 'stylus-loader']}
        ]
    },

    // When importing a module whose path matches one of the following, just
    // assume a corresponding global variable exists and use that instead.
    // This is important because it allows us to avoid bundling all of our
    // dependencies, which allows browsers to cache those libraries between builds.
    externals: {
        "react": "React",
        "react-dom": "ReactDOM"
    },
    plugins: [
        new webpack.NamedModulesPlugin()
    ]
};