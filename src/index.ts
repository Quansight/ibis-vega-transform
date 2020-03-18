import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
// import { TVoilaTracker } from 'phoila/lib/tokens';
import { IbisVegaRenderer, MIME_TYPE } from './renderer';

/**
 * A plugin ID for the extension.
 */
const PLUGIN_ID = 'ibis-vega-transform:plugin';

/**
 * The JupyterLab plugin metadata.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: PLUGIN_ID,
  // optional: [INotebookTracker, TVoilaTracker],
  autoStart: true
};

/**
 * Activate the plugin. This adds a new renderer type to all notebook
 * rendermime registries that knows how to lazily fetch ibis transforms
 * from the server.
 */
function activate(
  _: JupyterFrontEnd,
  notebooks: INotebookTracker | null
  // voila: TVoilaTracker | null
) {
  // if (voila) {
  //   voila.widgetAdded.connect(async (_, widget) => {
  //     const session = widget.content.session;
  //     session.rendermime.addFactory(
  //       {
  //         safe: true,
  //         defaultRank: 50,
  //         mimeTypes: [MIME_TYPE],
  //         createRenderer: () =>
  //           new IbisVegaRenderer(
  //             async () => (await session.connected).kernel,
  //             false
  //           )
  //       },
  //       0
  //     );
  //   });
  // }

  if (notebooks) {
    notebooks.widgetAdded.connect((_, widget) => {
      widget.content.rendermime.addFactory(
        {
          safe: true,
          defaultRank: 50,
          mimeTypes: [MIME_TYPE],
          createRenderer: options =>
            new IbisVegaRenderer(
              options,
              async () => widget.context.sessionContext.session?.kernel,
              true
            )
        },
        0
      );
    });
  }
}

export default plugin;
