/**
 * Hand-written typings for some vega-dataflow APIs
 * that aren't exposed in the official typings.
 */
declare module 'vega-dataflow' {
  /**
   * Re-export the official ones.
   */
  import * as typings from 'vega-typings';

  /**
   * Also include a transform typing with extra data.
   */
  export class Transform implements typings.Transform {
    constructor(init: any, params: any);
    targets: any;
    set: any;
    skip: any;
    modified: any;
    parameters: any;
    marshall: any;
    evaluate: any;
    run: any;
  }

  /**
   * A function that ingests a data record into the vega dataflow.
   */
  export function ingest(datum: any): any;
}