from .record import BaseRecord, Record
from .inference import BaseInference, Inference
from .record_inference import RecordInference, InferenceRecord, RecordAndInference

# Rebuild Record
BaseRecord.model_rebuild()
Record.model_rebuild()

# Rebuild Inference
BaseInference.model_rebuild()
Inference.model_rebuild()

# Rebuild Record-Inference
RecordInference.model_rebuild()
InferenceRecord.model_rebuild()
RecordAndInference.model_rebuild()
