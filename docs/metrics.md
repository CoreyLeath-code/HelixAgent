# Evidence-bound metrics

This repository does not provide verified staging, Snowflake, SageMaker, or
provider-cost measurements. Those systems are not exercised by the governed
default runtime, so no production KPI, speed-up, or cost claim is published here.

## Reproducible local measurements

The deterministic autonomy control-loop benchmark remains documented in
[Benchmark methodology](BENCHMARKS.md). It measures local orchestration and
SQLite checkpoint overhead only.

Vector-operation timing is a separate experiment. Run it on the target machine
and retain the JSON artifact with the environment metadata:

~~~bash
python -m benchmarks.vector_ops --sizes 128 1024 10000 --warmup 10 --repetitions 100 --output vector-ops-results.json
~~~

| Backend | Result |
|---|---|
| NumPy default | <fill after running: python -m benchmarks.vector_ops> |
| Optional C++ ctypes interop | <fill after running: python -m benchmarks.vector_ops, when the shared library is available> |
| Pure-Python degradation path | <fill after running: python -m benchmarks.vector_ops> |

The benchmark reports measurements from that invocation. It makes no cross-host
comparison and does not present the C++ binding as faster than NumPy/BLAS.

## Observability surface

The FastAPI service exposes Prometheus metrics and OpenTelemetry instrumentation.
Those integration points are observable interfaces, not evidence of a deployed
telemetry pipeline or service-level objective.
