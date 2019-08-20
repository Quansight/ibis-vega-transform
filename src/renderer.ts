import { DocumentRegistry } from '@jupyterlab/docregistry';
import { IRenderMime } from '@jupyterlab/rendermime';
import { Widget } from '@phosphor/widgets';

import * as vega from 'vega';
import vegaEmbed from 'vega-embed';

import ibisTransform from './transform';
import { compileSpec } from './compiler';


const MIMETYPE = 'application/vnd.vega.ibis.v5+json';

const TRANSFORM = 'queryibis';

export class VegaIbisRenderer extends Widget implements IRenderMime.IRenderer {
  constructor(
    private _context: DocumentRegistry.IContext<DocumentRegistry.IModel>
  ) {
    super();
  }
  async renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    const vlSpec = model.data[MIMETYPE] as any;
    const kernel = this._context.session.kernel;

    if (kernel === null) {
      return;
    }
    if (this._view) {
      this._view.finalize();
      this._view = null;
    }

    ibisTransform.kernel = kernel;
    const vSpec = await compileSpec(kernel, vlSpec);
    const res = await vegaEmbed(this.node, vSpec, {
      actions: true,
      defaultStyle: true,
      mode: 'vega'
    });
    this._view = res.view;
  }

  get isDisposed(): boolean {
    return this._isDisposed;
  }

  dispose(): void {
    this._isDisposed = true;
    if (this._view) {
      this._view.finalize();
      this._view = null;
    }
  }

  private _isDisposed = false;
  private _view: vega.View | null = null;
}