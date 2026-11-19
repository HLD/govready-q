const TerserPlugin = require("terser-webpack-plugin");
const dev = process.env.NODE_ENV !== 'production';

let config = {
  watchOptions: {
    poll: true,
    ignored: /node_modules/
  },
  devtool: dev ? 'eval-cheap-module-source-map' : false,
  plugins: [],
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin()],
    splitChunks: {
      cacheGroups: {
        styles: {
          name: 'styles',
          test: /\.css$/,
          chunks: 'all',
          enforce: true
        },
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    },
    runtimeChunk: {
      name: 'manifest'
    }
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {

          loader: 'babel-loader',
        },
      },
      {
        test: /\.css$/,
        use: ["style-loader", 'css-loader'] //MiniCssExtractPlugin.loader
      },
      {
        test: /\.(jpg|jpeg|png|woff|woff2|eot|ttf|svg)$/,
        type: 'asset',
        parser: { dataUrlCondition: { maxSize: 50000 } },
      }
    ]
  }
}

if(dev){
  const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
  config.plugins.push(new BundleAnalyzerPlugin())
}

module.exports = config;
