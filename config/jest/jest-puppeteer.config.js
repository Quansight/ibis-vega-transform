/**
 * @license BSD-3-Clause
 *
 * Copyright (c) 2019 Project Jupyter Contributors.
 * Distributed under the terms of the 3-Clause BSD License.
 */

const config = {
  launch: {
    headless: false,
    slowMo: process.env.SLOWMO === 'true'
    // executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  },
  // https://github.com/smooth-code/jest-puppeteer/tree/master/packages/jest-dev-server#options
  server: {
    command: "jupyter lab --port 8081 --no-browser --LabApp.token=''",
    port: 8081,
    launchTimeout: 10 * 1000
  }
};

/**
 * Exports.
 */
module.exports = config;
