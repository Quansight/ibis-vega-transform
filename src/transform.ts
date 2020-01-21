import { Kernel } from '@jupyterlab/services';
import { JSONObject, PromiseDelegate } from '@phosphor/coreutils';
import * as vega from 'vega';
import * as dataflow from 'vega-dataflow';
import { client } from 'jupyter-jaeger';

/**
 * Tries parsing all string values as dates.  Any that cannot be parsed are left alone
 *
 * https://github.com/Quansight/jupyterlab-omnisci/pull/85#issuecomment-519656950
 */
function parseDates(o: { [key: string]: any }): { [key: string]: any } {
  const n: { [key: string]: any } = {};
  for (const key in o) {
    const value = o[key];
    let parsed;
    if (typeof value === 'string') {
      parsed = Date.parse(o[key] as any);
      if (isNaN(parsed)) {
        parsed = value;
      }
    } else {
      parsed = value;
    }
    n[key] = parsed;
  }
  return n;
}

async function getData(parameters: any): Promise<any> {
  const { tracing } = QueryIbis;
  const spanExtract = tracing
    ? await client.startSpanExtract({
        name: 'transform',
        relationship: 'follows_from',
        reference: parameters.span
      })
    : null;

  const kernel = QueryIbis.kernel;
  if (!kernel) {
    console.error('Not connected to kernel');
    return;
  }

  const commSpan = tracing
    ? await client.startSpan({
        name: 'comm:queryibis',
        reference: spanExtract!,
        relationship: 'child_of'
      })
    : null;

  // Fetch the query results from the kernel.
  const comm = kernel.connectToComm('queryibis');

  const resultPromise = new PromiseDelegate<JSONObject[]>();
  comm.onMsg = msg =>
    resultPromise.resolve((msg.content.data as any) as JSONObject[]);

  // set span inside comm to be this comm message instead of root span
  if (tracing) {
    parameters = { ...parameters, span: await client.injectSpan(commSpan!) };
  }

  await comm.open(parameters).done;
  const result: JSONObject[] = await resultPromise.promise;

  if (tracing) {
    await client.finishSpan(commSpan!);
  }
  const parsedResult = result.map(parseDates);

  if (tracing) {
    await client.finishSpan(spanExtract!);
  }
  return parsedResult;
}

const TRANSFORM = 'queryibis';

/**
 * Generates a function to query data from an OmniSci Core database.
 * @param {object} params - The parameters for this operator.
 *
 * Inspired by load transform
 * https://github.com/vega/vega/blob/master/packages/vega-transforms/src/Load.js
 */
class QueryIbis extends dataflow.Transform implements vega.Transform {
  constructor(params: any) {
    super([], params);
    this._pending = null;
  }

  /**
   * The current kernel instance for the QueryIbis transform.
   */
  static kernel: Kernel.IKernelConnection | null;

  /**
   * Whether to record traces
   */
  static tracing: boolean;

  /**
   * The definition for the transform. Used by the vega dataflow logic
   * to decide how to use the transform.
   */
  /* tslint:disable-next-line */
  static readonly Definition = {
    type: 'QueryIbis',
    metadata: { changes: true, source: true },
    params: [
      {
        name: 'name',
        type: 'string',
        required: true
      },
      {
        name: 'data',
        type: 'expr',
        required: false
      },
      {
        name: 'transform',
        type: 'transform',
        array: true,
        required: false
      },
      {
        name: 'span',
        type: 'object',
        required: false
      }
    ]
  };

  transform(parameters: any, pulse: any): any {
    if (this._pending) {
      // update state and return pulse
      return this.output(pulse, this._pending);
    }

    // return promise for non-blocking async loading
    const p = getData(parameters).then(res => {
      this._pending = res;
      return (df: any) => df.touch(this);
    });
    return { async: p };
  }

  /**
   * Copied from
   * https://github.com/vega/vega/blob/d5b979955f67c9557b97eb5ddebb3fef48fe736c/packages/vega-transforms/src/Load.js#L52-L59
   */
  output(pulse: any, data: any) {
    data.forEach(dataflow.ingest);
    const out = pulse.fork(pulse.NO_FIELDS & pulse.NO_SOURCE);
    out.rem = this.value;
    this.value = out.source = out.add = data;
    this._pending = null;
    return out;
  }

  private _pending: Promise<any> | null;
  private value: any;
}

export default QueryIbis;

// Get the vega singleton and add our custom transform to it.
(vega as any).transforms[TRANSFORM] = QueryIbis;
