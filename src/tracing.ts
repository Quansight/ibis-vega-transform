import { initTracer } from 'jaeger-client';
import { Tracer } from 'opentracing';

export const tracer: Tracer = initTracer(
  {
    serviceName: 'ibis_vega_transform',
    sampler: { type: 'const', param: 1 },
    reporter: { collectorEndpoint: 'http://localhost:14268/api/traces' }
  },
  {}
);
