import { DocumentRegistry } from '@jupyterlab/docregistry';

import { IRenderMime } from '@jupyterlab/rendermime';

import { Widget } from '@phosphor/widgets';

import * as vega from 'vega';

import { compileSpec } from './compiler';

import ibisTransform from './transform';

export const MIME_TYPE = 'application/vnd.vega.ibis.v5+json';

export class IbisVegaRenderer extends Widget implements IRenderMime.IRenderer {
  constructor(
    private _context: DocumentRegistry.IContext<DocumentRegistry.IModel>
  ) {
    super();
  }
  async renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    const vlSpec = model.data[MIME_TYPE] as any;
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
    this._view = new vega.View(vega.parse(vSpec)).initialize(this.node);
    await this._view.runAsync();
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
