import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { INotebookTracker } from '@jupyterlab/notebook';
import { IbisVegaRenderer, MIME_TYPE } from './renderer';


/**
 * A plugin ID for the extension.
 */
 const PLUGIN_ID = 'ibis_vega_transform:plugin';

 /**
  * The JupyterLab plugin metadata.
  */
 const extension: JupyterFrontEndPlugin<void> = {
   activate,
   id: PLUGIN_ID,
   requires: [INotebookTracker],
   autoStart: true
 };

 /**
  * Activate the plugin. This adds a new renderer type to all notebook
  * rendermime registries that knows how to lazily fetch ibis transforms
  * from the server.
  */
 function activate(_: JupyterFrontEnd, notebooks: INotebookTracker) {
   notebooks.widgetAdded.connect((_, widget) => {
     widget.content.rendermime.addFactory(
       {
         safe: true,
         defaultRank: 50,
         mimeTypes: [MIME_TYPE],
         createRenderer: () =>
           new IbisVegaRenderer(
             async () => widget.context.sessionContext.session?.kernel,
             true
           )
       },
       0
     );
   });
 }

 export default extension;
