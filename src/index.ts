import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { INotebookTracker } from '@jupyterlab/notebook';

import { MIME_TYPE, IbisVegaRenderer } from './renderer';

const PLUGIN_ID = 'ibis-vega-transform:plugin';

const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: PLUGIN_ID,
  requires: [INotebookTracker],
  autoStart: true
};

function activate(_: JupyterFrontEnd, notebooks: INotebookTracker) {
  notebooks.widgetAdded.connect((_, { context, content }) => {
    content.rendermime.addFactory(
      {
        safe: true,
        defaultRank: 50,
        mimeTypes: [MIME_TYPE],
        createRenderer: () => new IbisVegaRenderer(context)
      },
      0
    );
  });
}

export default plugin;
