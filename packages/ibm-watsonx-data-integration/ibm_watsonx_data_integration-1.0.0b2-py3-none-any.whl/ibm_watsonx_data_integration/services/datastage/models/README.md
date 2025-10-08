This directory contains design prototypes and is meant to be temporary.



- FlowBuilder (user interacts with this)
- DAG (user indirectly mutates this)
- PipelineGenerator, FlowGenerator (DAG in), NodeGenerator, LinkGenerator
  - Circular flows, node input/output validation
- Pydantic models (JSON)
  - PipelineSchema
  - NodeSchema
  - InputLinkSchema, OutputSchema, StageNamePropertySchema
