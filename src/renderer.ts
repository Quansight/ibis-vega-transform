import { DocumentRegistry } from '@jupyterlab/docregistry';

import { IRenderMime } from '@jupyterlab/rendermime';

import { Widget } from '@phosphor/widgets';

import * as vega from 'vega';

import { compileSpec } from './compiler';

import ibisTransform from './transform';

export const MIME_TYPE = 'application/vnd.vega.ibis.v5+json';

/**
 * An alternative vega renderer that can query the server for lazy
 * evaluations of ibis expressions targeting SQL-like backends.
 */
export class IbisVegaRenderer extends Widget implements IRenderMime.IRenderer {
  /**
   * Construct a new renderer.
   */
  constructor(
    private _context: DocumentRegistry.IContext<DocumentRegistry.IModel>
  ) {
    super();
  }
  
  /**
   * Render vega data using the alternative renderer.
   */
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

    // TODO: is this safe if there are multiple kernels trying to use
    // the transform? Can we construct individual transforms/comms for
    // each renderer? What does IPywidgets do?
    ibisTransform.kernel = kernel;
    const vSpec = await compileSpec(kernel, vlSpec);
    this._view = new vega.View(vega.parse(vSpec)).initialize(this.node);
    await this._view.runAsync();
  }

  /**
   * Whether the renderer has been disposed.
   */
  get isDisposed(): boolean {
    return this._isDisposed;
  }

  /**
   * Dispose of the resources held by the renderer.
   */
  dispose(): void {
    this._isDisposed = true;
    // Vega needs to release its hooks into the DOM, otherwise it can eat up
    // a huge amount of the event loop.
    if (this._view) {
      this._view.finalize();
      this._view = null;
    }
  }

  private _isDisposed = false;
  private _view: vega.View | null = null;
}
