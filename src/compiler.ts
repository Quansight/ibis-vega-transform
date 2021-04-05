import { Kernel } from '@jupyterlab/services';
import { PromiseDelegate } from '@lumino/coreutils';
import { compile, normalize, TopLevelSpec } from 'vega-lite';
import { initConfig } from 'vega-lite/build/src/config';
import { mergeDeep } from 'vega-lite/build/src/util';
import * as themes from 'vega-themes';

import { extractTransforms } from './transformextract';
const COMM_ID = 'ibis_vega_transform:compiler';

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
  // For some reason we have to manually merge in the theme, like this used to do in the vega lite compiler
  // otherwise it will generate an incorrect black background on a white theme
  // https://github.com/vega/vega-lite/commit/7f5969ffefc35e3d583b0dec4b05bc14870747b4
  const theme = (vlSpec.usermeta?.embedOptions as
    | { theme?: string }
    | undefined)?.theme;
  if (theme) {
    // @ts-ignore
    mergeDeep(vlSpec, themes[theme]);
  }
  // uses same logic as
  // https://github.com/vega/vega-lite/blob/a4ee4ec393d86b611f95486ad2e1902bfa3ed0cf/test/transformextract.test.ts#L133

  const config = initConfig(vlSpec.config || {});
  const extractSpec = extractTransforms(
    normalize(vlSpec as any, config),
    config
  );
  console.log('Extracted Vega-Lite Spec', vlSpec);
  const vSpec = compile(extractSpec as any, { config }).spec;

  // Change vega transforms to ibis transforms on the server side.
  const transformedSpecPromise = new PromiseDelegate<any>();
  const comm = kernel.createComm(COMM_ID);
  comm.onMsg = msg => transformedSpecPromise.resolve(msg.content.data);
  await comm.open({ spec: vSpec, span, rootSpan } as any).done;
  const finalSpec = await transformedSpecPromise.promise;
  return finalSpec;
}
