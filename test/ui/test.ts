/**
 * @license BSD-3-Clause
 *
 * Copyright (c) 2019 Project Jupyter Contributors.
 * Distributed under the terms of the 3-Clause BSD License.
 */

const fs = require('fs');
const { setDefaultOptions } = require('expect-puppeteer');

// Extend the time allowed for tests to complete:
const timeout = 5 * 60 * 1000;
jest.setTimeout(timeout);
setDefaultOptions({ timeout });

/**
 * Set the default download folder for the browser
 *
 * @private
 */
async function setDownloadFolder(folder: string) {
  // Create folder for saved images
  const dir = './images';
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir);
  }

  const dirExample = './images/' + folder;
  if (!fs.existsSync(dirExample)) {
    fs.mkdirSync(dirExample);
  }

  // Set the download folder for the browser
  await (page as any)._client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: dirExample
  });
}

/**
 * Returns a promise for suspending stack execution for a specified duration.
 *
 * @private
 * @param ms - duration (in milliseconds)
 * @returns promise
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Click on submenu for a give menu.
 *
 * @private
 * @param menuString - Name of menu (File, Run...)
 * @param itemString - Name of submenu (Run All Cells...)
 */
async function clickMenuItem(menuString: string, itemString: string) {
  let menuItems: { [index: string]: any } = {
    File: {
      'Close and Shutdown': { child: 14, popup: 'OK' },
      'Save Notebook': { child: 18, popup: '' }
    },
    Run: {
      'Run All Cells': { child: 17, popup: '' }
    },
    Kernel: {
      'Restart Kernel and Clear All Outputs': { child: 6, popup: 'Restart' }
    }
  };
  const childNumber = menuItems[menuString][itemString]['child'];
  const popupReply = menuItems[menuString][itemString]['popup'];

  // Click on menu matching menuString
  await expect(page).toClick('.p-MenuBar-itemLabel', { text: menuString });

  // Wait for pop up menu to appear
  await page.waitForFunction(
    () => !!document.querySelector('.p-MenuBar-menu') !== null,
    {}
  );
  // await page.waitFor(2000);

  await expect(page).toClick(
    `.p-MenuBar-menu > ul > li:nth-child(${childNumber})`
  );

  if (popupReply) {
    await page.waitForFunction(
      () => !!document.querySelector('.jp-Dialog-content') !== null,
      {}
    );
    // await page.waitFor(2000);
    await expect(page).toClick('button', { text: popupReply });
    await page.waitFor(5000);
  }
}

/**
 * Check that a given prompt number is found on current open notebook
 *
 * @private
 * @param promptNumber - the prompt number to look for
 * @returns bool
 */
function checkForPrompt(promptNumber: number) {
  const elements: Element[] = Array.from(
    document.querySelectorAll('.jp-OutputArea-prompt')
  );
  const promptString: string = `[${promptNumber}]:`;
  const hasPrompt = (element: Element) =>
    (<HTMLElement>element).innerText == promptString;
  return elements.some(hasPrompt);
}

/**
 * Checks that a notebook tab with given tabName has been loaded.
 *
 * @private
 * @param tabName - the name of the notebook expected to appear on the tab
 */
function checkForNotebookTabName(tabName: string) {
  // TODO
  const tabs: Element[] = Array.from(
    document.querySelectorAll('.p-DockPanel-tabBar li')
  );
  const hasName = (element: Element) =>
    (<HTMLElement>element).innerText == tabName;
  return tabs.some(hasName);
}

describe('Test Ibis-Vega-Transform', () => {
  beforeAll(async () => {
    // Load JupyterLab:
    // await page.goto('http://localhost:8080/lab?reset');
    // // NOTE: depending on system resource constraints, this may NOT be enough time for JupyterLab to load and get "settled", so to speak. If CI tests begin inexplicably failing due to timeout failures, may want to consider increasing the sleep duration...
    // await sleep(5 * 1000);
  });

  it.each([
    // File name, Expected max output prompt, timeout (ms)
    ['charting-example', 2, 60 * 1000],
    // ['ibis-altair-extraction', 8, 30 * 1000],    // FAIL: enable after fix
    // ['interactive-slider.ipynb', 0, 10 * 1000],  // FAIL: enable after fix
    ['omnisci-vega-example', 3, 10 * 1000],
    ['vega-compiler', 6, 10 * 1000]
  ])(
    'should open notebook correctly',
    async (file, promptNumber, maxTimeout) => {
      expect.assertions(8);
      // await page.goto('http://localhost:8080/lab?reset');

      // NOTE: depending on system resource constraints, this may NOT be enough time for JupyterLab to load and get "settled", so to speak. If CI tests begin inexplicably failing due to timeout failures, may want to consider increasing the sleep duration...

      console.log(`\nRunning "${file}.ipynb"\n`);

      // Go to specific notebook file
      await page.goto(`http://localhost:8080/lab/tree/examples/${file}.ipynb`);
      await page.waitForFunction(
        checkForNotebookTabName,
        { timeout: maxTimeout as number },
        `${file}.ipynb`
      );

      await sleep(5 * 1000);

      // Restart kernel and clear output
      await clickMenuItem('Kernel', 'Restart Kernel and Clear All Outputs');

      // Run all cells in otebooks
      await clickMenuItem('Run', 'Run All Cells');
      await page.waitForFunction(
        checkForPrompt,
        { timeout: maxTimeout as number },
        promptNumber
      );

      // Charts take a little while to appear after the output number prompt has appeared
      await page.waitFor(5 * 1000);

      // Close and shutdown
      await clickMenuItem('File', 'Close and Shutdown');
      await page.waitFor(4 * 1000);
    }
  );
});
