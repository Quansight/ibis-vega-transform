import { IRenderMime } from '@jupyterlab/rendermime';
import { Widget } from '@phosphor/widgets';
import * as vega from 'vega';
import vegaEmbed from 'vega-embed';
import { compileSpec } from './compiler';
import ibisTransform from './transform';
import { client } from 'jupyter-jaeger';
import { Kernel } from '@jupyterlab/services';

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
    private getKernel: () => Promise<Kernel.IKernelConnection | null>
  ) {
    super();
  }

  /**
   * Render vega data using the alternative renderer.
   */
  async renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    const { spec: vlSpec, span: injectedSpan } = model.data[MIME_TYPE] as {
      spec: any;
      span: object;
    };
    const renderModelSpan = await client.startSpanExtract({
      name: 'renderModel',
      reference: injectedSpan,
      relationship: 'follows_from'
    });
    const kernel = await this.getKernel();

    if (kernel === null) {
      return;
    }

    // Skip rendering if we are already rendering or we are about to rerender the same spec
    if (
      this._renderingSpec ||
      // TODO: Replace this with real deep equality
      (this._renderedSpec &&
        JSON.stringify(this._renderedSpec) === JSON.stringify(vlSpec))
    ) {
      return;
    }
    this._renderingSpec = true;

    if (this._view) {
      this._view.finalize();
      this._view = null;
    }

    const compileSpecSpan = await client.startSpan({
      name: 'compileSpec',
      reference: renderModelSpan,
      relationship: 'child_of'
    });

    const vSpec = await compileSpec(
      kernel,
      vlSpec,
      await client.injectSpan(compileSpecSpan),
      injectedSpan
    );

    await client.finishSpan(compileSpecSpan);

    const vegaEmbedSpan = await client.startSpan({
      name: 'vegaEmbed',
      reference: renderModelSpan,
      relationship: 'child_of'
    });

    // TODO: is this safe if there are multiple kernels trying to use
    // the transform? Can we construct individual transforms/comms for
    // each renderer? What does IPywidgets do?
    ibisTransform.kernel = kernel;
    const res = await vegaEmbed(this.node, vSpec, {
      actions: true,
      defaultStyle: true,
      mode: 'vega'
    });
    this._view = res.view;

    await client.finishSpan(vegaEmbedSpan);

    this._renderingSpec = false;
    this._renderedSpec = vlSpec;
    await client.finishSpan(renderModelSpan);
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
  private _renderingSpec = false;
  private _renderedSpec: any = null;
}
