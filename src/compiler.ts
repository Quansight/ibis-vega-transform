import { Kernel } from '@jupyterlab/services';
import { PromiseDelegate } from '@lumino/coreutils';
import { compile, extractTransforms, normalize, TopLevelSpec } from 'vega-lite';
import { initConfig } from 'vega-lite/build/src/config';

const COMM_ID = 'ibis-vega-transform:compiler';

/**
 * Takes in a Vega-Lite spec and returns a compiled Vega spec,
 * with the Vega transforms swapped out for Ibis transforms.
 */
export async function compileSpec(
  kernel: Kernel.IKernelConnection,
  vlSpec: TopLevelSpec,
  span: any,
  rootSpan: any
): Promise<object> {
  // uses same logic as
  // https://github.com/vega/vega-lite/blob/a4ee4ec393d86b611f95486ad2e1902bfa3ed0cf/test/transformextract.test.ts#L133

  const config = initConfig(vlSpec.config || {});
  const extractSpec = extractTransforms(
    normalize(vlSpec as any, config),
    config
  );
  // TODO: Log extracted vl spec
  const vSpec = compile(extractSpec as any, { config }).spec;

  // Change vega transforms to ibis transforms on the server side.
  const transformedSpecPromise = new PromiseDelegate<any>();
  const comm = kernel.createComm(COMM_ID);
  comm.onMsg = msg => transformedSpecPromise.resolve(msg.content.data);
  await comm.open({ spec: vSpec, span, rootSpan } as any).done;
  const finalSpec = await transformedSpecPromise.promise;
  return finalSpec;
}
