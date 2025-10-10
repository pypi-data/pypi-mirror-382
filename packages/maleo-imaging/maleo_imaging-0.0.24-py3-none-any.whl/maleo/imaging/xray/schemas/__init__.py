from .record import RecordCoreSchema, RecordCompleteSchema
from .inference import (
    GenericInferenceCoreSchema,
    MultiFindingInferenceCoreSchema,
    TuberculosisInferenceCoreSchema,
    GenericInferenceCompleteSchema,
    MultiFindingInferenceCompleteSchema,
    TuberculosisInferenceCompleteSchema,
)
from .record_inference import (
    RecordInferenceSchema,
    InferenceRecordSchema,
    RecordAndInferenceSchema,
)

# Rebuild Record
RecordCoreSchema.model_rebuild()
RecordCompleteSchema.model_rebuild()

# Rebuild Inference
GenericInferenceCoreSchema.model_rebuild()
MultiFindingInferenceCoreSchema.model_rebuild()
TuberculosisInferenceCoreSchema.model_rebuild()
GenericInferenceCompleteSchema.model_rebuild()
MultiFindingInferenceCompleteSchema.model_rebuild()
TuberculosisInferenceCompleteSchema.model_rebuild()

# Rebuild Record-Inference
RecordInferenceSchema.model_rebuild()
InferenceRecordSchema.model_rebuild()
RecordAndInferenceSchema.model_rebuild()
