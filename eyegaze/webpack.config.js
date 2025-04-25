const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');

const isDevelopment = process.env.NODE_ENV !== 'production';

module.exports = [
  // Main process
  {
    mode: isDevelopment ? 'development' : 'production',
    entry: {
      main: './src/main/main.ts',
      preload: './src/main/preload.ts'
    },
    target: 'electron-main',
    resolve: {
      extensions: ['.ts', '.js'],
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@main': path.resolve(__dirname, 'src/main'),
        '@common': path.resolve(__dirname, 'src/common'),
        '@ai': path.resolve(__dirname, 'src/ai'),
        '@virtualcam': path.resolve(__dirname, 'src/virtualcam'),
        '@notes': path.resolve(__dirname, 'src/notes')
      }
    },
    module: {
      rules: [
        {
          test: /\.ts$/,
          include: /src/,
          use: [{ loader: 'ts-loader' }]
        },
        {
          test: /\.node$/,
          use: 'node-loader',
        }
      ]
    },
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'main/[name].js'
    },
    devtool: isDevelopment ? 'source-map' : false,
    node: {
      __dirname: false
    }
  },
  
  // Renderer process
  {
    mode: isDevelopment ? 'development' : 'production',
    entry: './src/renderer/index.tsx',
    target: 'electron-renderer',
    resolve: {
      extensions: ['.ts', '.tsx', '.js', '.jsx'],
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@renderer': path.resolve(__dirname, 'src/renderer'),
        '@common': path.resolve(__dirname, 'src/common'),
        '@ai': path.resolve(__dirname, 'src/ai'),
        '@virtualcam': path.resolve(__dirname, 'src/virtualcam'),
        '@notes': path.resolve(__dirname, 'src/notes')
      }
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          include: /src/,
          use: [{ loader: 'ts-loader' }]
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader']
        },
        {
          test: /\.(png|jpg|gif|svg)$/,
          type: 'asset/resource'
        }
      ]
    },
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'renderer/index.js'
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: './src/renderer/index.html',
        filename: '../index.html'
      }),
      new CopyPlugin({
        patterns: [
          { 
            from: 'assets', 
            to: 'assets',
            noErrorOnMissing: true
          }
        ]
      })
    ],
    devtool: isDevelopment ? 'source-map' : false
  }
]; 