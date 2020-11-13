/**
 * @license BSD-3-Clause
 *
 * Copyright (c) 2019 Project Jupyter Contributors.
 * Distributed under the terms of the 3-Clause BSD License.
 */

const fs = require('fs');
const path = require('path');
const compare = require('resemblejs').compare;

const { setDefaultOptions } = require('expect-puppeteer');

// Extend the time allowed for tests to complete:
const timeout = 10 * 60 * 1000;
jest.setTimeout(timeout);
setDefaultOptions({ timeout });

/**
 * Set the default download folder for the browser
 *
 * @private
 */
async function setDownloadFolder(base: string, folder: string) {
  // Create folder for saved images
  const dir: string = path.join(__dirname, base);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir);
  }

  const folderPath: string = path.join(__dirname, base, folder);
  if (!fs.existsSync(folderPath)) {
    fs.mkdirSync(folderPath);
  }

  // Set the download folder for the browser
  await (page as any)._client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: folderPath
  });
  return folderPath;
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
    'li[class="lm-MenuBar-item p-MenuBar-item"]',
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
 * Save charts in notebook
 *
 * @param file
 * @param dirExample
 */
async function saveCharts(dirExample: string) {
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
    let renamedImage: string = path.join(dirExample, `${index}.svg`);
    console.log(`File saved at: ${savedImage}`);
    console.log(`File renamed to: ${renamedImage}`);
    fs.rename(savedImage, renamedImage, (err: Error) => {
      if (err) {
        console.log(err);
      }
    });
  }
}

/**
 * Save charts in notebook
 *
 * @param file
 * @param dirExample
 */
async function compareCharts(
  dirExample: string,
  dirOriginal: string,
  threshold: number
) {
  const originalFiles = fs.readdirSync(dirOriginal);
  const computedFiles = fs.readdirSync(dirExample);
  const options = {
    // stop comparing once determined to be > 5% non-matching; this will
    // also enable compare-only mode and no output image will be rendered;
    // the combination of these results in a significant speed-up in batch processing
    returnEarlyThreshold: 5
  };
  let results = [];

  for (let index = 0; index < originalFiles.length; index++) {
    let image1 = path.join(dirOriginal, originalFiles[index]);
    let image2 = path.join(dirExample, computedFiles[index]);

    console.log(`Comparing images: "${index}.svg"`);
    console.log(image1);
    console.log(image2);

    // The parameters can be Node Buffers
    // data is the same as usual with an additional getBuffer() function
    compare(image1, image2, options, function(err, data) {
      if (err) {
        console.log('An error!');
      } else {
        console.log(data);
        results.push(data['rawMisMatchPercentage']);
      }
    });
  }
  return results;
}

describe('Test Ibis-Vega-Transform', () => {
  it.each([
    // File name, chart amount, timeout (ms)
    ['charting-example', 7, 60 * 1000],
    ['ibis-altair-extraction', 4, 40 * 1000],
    ['interactive-slider', 1, 10 * 1000],
    ['omnisci-vega-example', 1, 15 * 1000],
    ['performance-charts', 2, 15 * 1000],
    ['vega-compiler', 4, 60 * 1000]
  ])(
    'should open and run notebook correctly',
    async (file, chartAmount, maxTimeout) => {
      console.log(`\n\n## Running "${file}.ipynb"\n`);

      // Go to specific notebook file
      await page.goto(`http://localhost:8080/lab/tree/examples/${file}.ipynb`);
      await page.waitForSelector(
        '.lm-DockPanel-tabBar li[data-type="document-title"]'
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

      // Check amount of charts is correct
      const createdCharts = await page.$$('.vega-embed > details > summary');
      expect(createdCharts.length).toBe(chartAmount);
      console.log(`Found charts: ${createdCharts.length}`);
      await page.waitFor(2 * 1000);

      // Set download folder
      let folderPath: string = await setDownloadFolder(
        '/../../../images',
        file as string
      );
      console.log(`Setting download folder: ${folderPath}`);

      // Wait to make sure all images appeared
      await sleep(maxTimeout / 2);

      // Save images
      await saveCharts(folderPath);
      await page.waitFor(2 * 1000);

      // Check amount of files saved is correct
      const amountOfFile = fs.readdirSync(folderPath);
      expect(amountOfFile.length).toBe(chartAmount);

      // Compare images
      let threshold = 1.0;
      let originalImagesPath: string = await setDownloadFolder(
        '/../../images',
        file as string
      );
      console.log(`Original images folder: ${originalImagesPath}`);
      let results = await compareCharts(
        folderPath,
        originalImagesPath,
        threshold
      );
      const isBelowThreshold = value => value < threshold;
      expect(results.every(isBelowThreshold)).toBe(true);
      await page.waitFor(2 * 1000);

      // Close dialog "Are you sure you want to leave..."
      page.on('dialog', async dialog => {
        console.log(dialog.message()); // outputs: ''
        await dialog.dismiss();
      });

      // Close and shutdown
      await clickMenuItem('File', 'Close and  Shutdown Notebook');
      await page.waitFor(4 * 1000);
    }
  );
});
