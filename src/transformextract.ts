/**
 * Used to be in Vega Lite, but removed in version 4.14.0
 *
 * https://github.com/vega/vega-lite/blob/7b6e0d203f1a9293747aaeda3e637bae753d5fcf/src/transformextract.ts
 */

import { Config } from 'vega-lite/build/src/config';
import { extractTransformsFromEncoding } from 'vega-lite/build/src/encoding';
import { NormalizedSpec } from 'vega-lite/build/src/spec';
import { SpecMapper } from 'vega-lite/build/src/spec/map';
import { GenericUnitSpec } from 'vega-lite/build/src/spec/unit';

class TransformExtractMapper extends SpecMapper<
  { config: Config },
  GenericUnitSpec<any, any>
> {
  public mapUnit(
    spec: GenericUnitSpec<any, any>,
    { config }: { config: Config }
  ) {
    if (spec.encoding) {
      const { encoding: oldEncoding, transform: oldTransforms } = spec;
      const {
        bins,
        timeUnits,
        aggregate,
        groupby,
        encoding
      } = extractTransformsFromEncoding(oldEncoding, config);

      const transform = [
        ...(oldTransforms ? oldTransforms : []),
        ...bins,
        ...timeUnits,
        ...(aggregate.length === 0 ? [] : [{ aggregate, groupby }])
      ];

      return {
        ...spec,
        ...(transform.length > 0 ? { transform } : {}),
        encoding
      };
    } else {
      return spec;
    }
  }
}

const extractor = new TransformExtractMapper();

/**
 * Modifies spec extracting transformations from encoding and moving them to the transforms array
 */
export function extractTransforms(
  spec: NormalizedSpec,
  config: Config
): NormalizedSpec {
  return extractor.map(spec, { config });
}
