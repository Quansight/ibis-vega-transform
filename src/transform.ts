import { Kernel } from '@jupyterlab/services';
import { JSONObject, PromiseDelegate } from '@phosphor/coreutils';
import * as vega from 'vega';
import * as dataflow from 'vega-dataflow';
import { startSpanExtract, finishSpan, startSpan, injectSpan } from './tracing';

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

const TRANSFORM = 'queryibis';

/**
 * Generates a function to query data from an OmniSci Core database.
 * @param {object} params - The parameters for this operator.
 */
class QueryIbis extends dataflow.Transform implements vega.Transform {
  constructor(params: any) {
    console.log(params);
    super([], params);
  }

  /**
   * The current kernel instance for the QueryIbis transform.
   */
  static kernel: Kernel.IKernelConnection | null;

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

  get value(): any {
    return this._value;
  }
  set value(val: any) {
    this._value = val;
  }

  async transform(parameters: any, pulse: any): Promise<any> {

    const spanExtract = await startSpanExtract({
      name: 'transform',
      relationship: 'follows_from',
      reference: parameters.span
    });

    const kernel = QueryIbis.kernel;
    if (!kernel) {
      console.error('Not connected to kernel');
      return;
    }

    const commSpan = await startSpan({
      name: 'comm:queryibis',
      reference: spanExtract,
      relationship: 'child_of'
    });

    // Fetch the query results from the kernel.
    const comm = kernel.connectToComm('queryibis');

    const resultPromise = new PromiseDelegate<JSONObject[]>();
    comm.onMsg = msg =>
      resultPromise.resolve((msg.content.data as any) as JSONObject[]);

    // set span inside comm to be this comm message instead of root span
    parameters.span = await injectSpan(commSpan);

    await comm.open(parameters).done;
    const result: JSONObject[] = await resultPromise.promise;

    await finishSpan(commSpan);

    const parsedResult = result.map(parseDates);

    // Ingest the data and push it into the dataflow graph.
    parsedResult.forEach(dataflow.ingest);

    /* tslint:disable-next-line */
    const out = pulse.fork(pulse.NO_FIELDS & pulse.NO_SOURCE);
    out.rem = this._value;
    this._value = out.add = out.source = parsedResult;

    await finishSpan(spanExtract);
    return out;
  }

  private _value: any;
}

export default QueryIbis;

// Get the vega singleton and add our custom transform to it.
(vega as any).transforms[TRANSFORM] = QueryIbis;
