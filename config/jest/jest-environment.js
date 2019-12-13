/**
 * @license BSD-3-Clause
 *
 * Copyright (c) 2019 Project Jupyter Contributors.
 * Distributed under the terms of the 3-Clause BSD License.
 */

// Based on from https://yarnpkg.com/en/package/@rws-air/jestscreenshot

const PuppeteerEnvironment = require('jest-environment-puppeteer-jsdom');

class CustomEnvironment extends PuppeteerEnvironment {
  async setup() {
    await super.setup();
  }
  async teardown() {
    await this.global.page.waitFor(2000);
    await super.teardown();
  }
}

/**
 * Exports.
 */
module.exports = CustomEnvironment;
