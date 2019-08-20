import { Kernel } from '@jupyterlab/services';

import { PromiseDelegate } from '@phosphor/coreutils';

import { TopLevelSpec, compile } from 'vega-lite';

const COMM_ID = 'ibis-vega-transform:compiler';

/**
 * Takes in a Vega-Lite spec and returns a compiled Vega spec,
 * with the Vega transforms swapped out for Ibis transforms.
 */
export async function compileSpec(
  kernel: Kernel.IKernelConnection,
  vlSpec: TopLevelSpec
): Promise<object> {
  // Compile vega-lite to vega
  const vSpec = compile(vlSpec).spec;

  // Change vega transforms to ibis transforms on the server side.
  const transformedSpecPromise = new PromiseDelegate<any>();
  const comm = kernel.connectToComm(COMM_ID);
  comm.onMsg = msg => transformedSpecPromise.resolve(msg.content.data);
  await comm.open(vSpec as any).done;
  return transformedSpecPromise.promise;
}
