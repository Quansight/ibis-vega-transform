import { Kernel } from '@jupyterlab/services';
import { JSONObject, PromiseDelegate } from '@lumino/coreutils';
import * as vega from 'vega';
import * as dataflow from 'vega-dataflow';
import { client } from 'jupyter_jaeger';

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

/**
 * The possible states our transform can be in.
 *
 * The idea here is that after a transform finished fetching data,
 * it saves that data on the instance and triggers a new round.
 *
 * When this new round hits, we know we just computed some data, so we can update it.
 *
 *
 * The tricky part is what if the user has an update while the data is being fetched?
 * In that case, we wanna stop fetching ASAP and abort that transaction.
 *
 * This is why we have the `aborted` property on the fetching state. We can set that to `true`
 * if we get a newer message before the data has been fetched, which should cause it to stop
 * and not return any results.
 *
 * This assumes that if the by calling `df.touch` the next cycle will be caused just by this
 * not by some user input.
 *
 * If this is not the case (if vega collapses cycles for performance) we should instead save some hash
 * of the parameters and verify they are equal to the current ones.
 */
const enum StateEnum {
  initial = 'initial',
  fetching = 'fetching',
  fetched = 'fetched'
}
// Add way to throw away data if wrong returned
type State =
  | { state: StateEnum.initial }
  | { state: StateEnum.fetching; aborted: boolean }
  | { state: StateEnum.fetched; data: Array<object> };

async function getData(
  parameters: any,
  abortSignal: { aborted: boolean }
): Promise<null | Array<object>> {
  const { tracing, kernel } = QueryIbis;
  if (!kernel) {
    throw new Error('Not connected to any kernel');
  }
  const spanExtract = tracing
    ? await client.startSpanExtract({
        name: 'transform',
        relationship: 'follows_from',
        reference: parameters.span
      })
    : null;

  const cleanup = async () => {
    if (tracing) {
      await client.finishSpan(spanExtract!);
    }
  };

  if (abortSignal.aborted) {
    await cleanup();
    return null;
  }

  // Fetch the query results from the kernel.
  const comm = kernel.createComm('queryibis');

  const resultPromise = new PromiseDelegate<JSONObject[]>();
  comm.onMsg = msg =>
    resultPromise.resolve((msg.content.data as any) as JSONObject[]);

  // set span inside comm to be this comm message instead of root span
  if (tracing) {
    parameters = { ...parameters, span: await client.injectSpan(spanExtract!) };
  }
  if (abortSignal.aborted) {
    await cleanup();
    return null;
  }

  await comm.open(parameters).done;

  if (abortSignal.aborted) {
    await cleanup();
    return null;
  }

  const result: JSONObject[] = await resultPromise.promise;
  if (abortSignal.aborted) {
    await cleanup();
    return null;
  }
  const parsedResult = result.map(parseDates);

  await cleanup();
  if (abortSignal.aborted) {
    return null;
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
    this._state = { state: StateEnum.initial };
  }

  /**
   * The current kernel instance for the QueryIbis transform.
   */
  static kernel: Kernel.IKernelConnection | undefined;

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
    if (this._state.state === StateEnum.fetched) {
      // update state and return pulse
      return this.output(pulse, this._state.data);
    }
    if (this._state.state === StateEnum.fetching) {
      this._state.aborted = true;
    }

    this._state = { state: StateEnum.fetching, aborted: false };

    // return promise for non-blocking async loading
    const p = getData(parameters, this._state).then(res => {
      if (res) {
        this._state = { state: StateEnum.fetched, data: res };
        return (df: any) => df.touch(this);
      }
      /* tslint:disable:no-empty */
      return () => {};
    });
    return { async: p };
  }

  /**
   * Copied from
   * https://github.com/vega/vega/blob/d5b979955f67c9557b97eb5ddebb3fef48fe736c/packages/vega-transforms/src/Load.js#L52-L59
   */
  output(pulse: any, data: any) {
    data.forEach(dataflow.ingest);
    // tslint:disable-next-line:no-bitwise
    const out = pulse.fork(pulse.NO_FIELDS & pulse.NO_SOURCE);
    out.rem = this.value;
    this.value = out.source = out.add = data;
    this._state = { state: StateEnum.initial };
    return out;
  }

  private _state: State;
  private value: any;
}

export default QueryIbis;

// Get the vega singleton and add our custom transform to it.
(vega as any).transforms[TRANSFORM] = QueryIbis;
