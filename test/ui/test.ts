/**
 * @license BSD-3-Clause
 *
 * Copyright (c) 2019 Project Jupyter Contributors.
 * Distributed under the terms of the 3-Clause BSD License.
 */

const fs = require('fs');
const path = require('path');
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
async function setDownloadFolder() {
  // Create folder for saved images
  const dir: string = path.join(__dirname, '/../../../images');
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir);
  }

  // Set the download folder for the browser
  await (page as any)._client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: dir
  });
  return dir;
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

async function getElement(selector: string, text: string) {
  const elements = await page.$$(selector);
  for (let element of elements) {
    const elementText = await page.evaluate(el => el.textContent, element);
    if (elementText.includes(text)) {
      // console.log(`[${elementText}]`);
      return element;
    }
  }
}

/**
 * Click on submenu for a given menu.
 *
 * @private
 * @param menuString - Name of menu (File, Run...)
 * @param itemString - Name of submenu (Run All Cells...)
 */
async function clickMenuItem(menuString: string, subMenuString: string) {
  let menuItems: { [index: string]: any } = {
    File: {
      'Close and  Shutdown Notebook': { popup: 'OK' },
      'Save Notebook': { popup: '' }
    },
    Edit: {
      'Clear All Outputs': { popup: '' }
    },
    Run: {
      'Run All Cells': { popup: '' }
    },
    Kernel: {
      'Restart Kernel and Clear All Outputs': { popup: 'Restart' },
      'Restart Kernel': { popup: 'Restart' }
    }
  };
  const popupReply = menuItems[menuString][subMenuString]['popup'];

  const menuElement = await getElement(
    'li[class="p-MenuBar-item"]',
    menuString
  );
  menuElement.click();
  await page.waitForSelector('.p-MenuBar-menu');
  await page.waitFor(1 * 1000);

  const subMenuElement = await getElement(
    '.p-MenuBar-menu > ul > li[data-type="command"]',
    subMenuString
  );
  await page.evaluate(el => (el.style.background = 'red'), subMenuElement);
  await page.waitFor(1 * 1000);
  await page.evaluate(el => (el.style.background = ''), subMenuElement);
  subMenuElement.click();

  if (popupReply) {
    await page.waitForFunction(
      () => document.querySelector('.jp-Dialog-content') !== null,
      {}
    );
    await page.waitFor(1 * 1000);
    const button = await getElement('button.jp-Dialog-button', popupReply);
    button.click();
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

function checkForVegaChartAmount(chartAmount: number) {
  const chartOptionButtons: Element[] = Array.from(
    document.querySelectorAll('.vega-embed > details > summary')
  );
  return chartOptionButtons.length == chartAmount;
}

/**
 *
 * @param file
 * @param dirExample
 */
async function saveCharts(file: string, dirExample: string) {
  let vegaMenus = await page.$$('.vega-embed > details > summary');
  let vegaMenuItems = await page.$$(
    '.vega-embed > details > div > a:nth-child(1)'
  );
  for (let index = 0; index < vegaMenus.length; index++) {
    vegaMenus[index].click();
    await page.waitFor(2 * 1000);
    vegaMenuItems[index].click();
    await page.waitFor(3 * 1000);

    // Rename file
    let savedImage: string = path.join(dirExample, 'visualization.svg');
    let renamedImage: string = path.join(dirExample, file + `-${index}.svg`);
    console.log(`File saved at: ${savedImage}`);
    console.log(`File renamed to:${renamedImage}`);
    fs.rename(savedImage, renamedImage, (err: Error) => {
      if (err) {
        console.log(err);
      }
    });
  }
}

describe('Test Ibis-Vega-Transform', () => {
  it.each([
    // File name, Expected max output prompt, chart amount, timeout (ms)
    // ['charting-example', 2, 1, 60 * 1000],
    // ['ibis-altair-extraction', 8, 30 * 1000],    // FAIL: enable after fix
    // ['interactive-slider.ipynb', 0, 10 * 1000],  // FAIL: enable after fix
    // ['omnisci-vega-example', 3, 1, 15 * 1000],
    ['vega-compiler', 6, 4, 10 * 1000]
  ])(
    'should open notebook correctly',
    async (file, promptNumber, chartAmount, maxTimeout) => {
      try {
        // expect.assertions(8);

        console.log(`\n\n## Running "${file}.ipynb"\n`);

        // Go to specific notebook file
        await page.goto(
          `http://localhost:8080/lab/tree/examples/${file}.ipynb`
        );
        await page.waitForSelector(
          '.p-DockPanel-tabBar li[data-type="document-title"]'
        );
        await sleep(5 * 1000);

        // Restart kernel and clear output
        await clickMenuItem('Kernel', 'Restart Kernel and Clear All Outputs');
        await page.waitFor(5 * 1000);

        // Run all cells in notebooks
        await clickMenuItem('Run', 'Run All Cells');
        await page.waitForFunction(
          checkForVegaChartAmount,
          { timeout: maxTimeout as number },
          chartAmount
        );

        // Check
        const createdCharts = await page.$$('.vega-embed > details > summary');
        expect(createdCharts.length).toBe(chartAmount);

        // Set download folder
        let dirExample: string = await setDownloadFolder();
        console.log(`Setting download folder ${dirExample}`);

        // Clicks and saves image
        await saveCharts(file as string, dirExample);

        // Close and shutdown
        await clickMenuItem('File', 'Close and  Shutdown Notebook');
        await page.waitFor(4 * 1000);
      } catch (e) {
        console.log(e);
      }
    }
  );
});
