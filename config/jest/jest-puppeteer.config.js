/**
 * @license BSD-3-Clause
 *
 * Copyright (c) 2019 Project Jupyter Contributors.
 * Distributed under the terms of the 3-Clause BSD License.
 */

const portNumber = 8080;
let browserExecutablePath = '';

// Use Chrome if running test suit locally
if (process.env.CI !== 'true') {
  browserExecutablePath =
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
}

const config = {
  launch: {
    headless: false,
    slowMo: process.env.SLOWMO === 'true',
    executablePath: browserExecutablePath,
    browserContext: 'incognito'
  },
  // https://github.com/smooth-code/jest-puppeteer/tree/master/packages/jest-dev-server#options
  server: {
    command: `jupyter lab --port ${portNumber} --no-browser --LabApp.token=''`,
    port: portNumber,
    launchTimeout: 10 * 1000
  }
};

/**
 * Exports.
 */
module.exports = config;
