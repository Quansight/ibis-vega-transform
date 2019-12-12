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
    try {
      await super.setup();
    } catch (e) {
      console.log(e);
    }
  }
  async teardown() {
    try {
      await this.global.page.waitFor(2000);
      await super.teardown();
    } catch (e) {
      console.log(e);
    }
  }
}

/**
 * Exports.
 */
module.exports = CustomEnvironment;
