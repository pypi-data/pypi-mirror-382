from .record import RecordCoreDTO, RecordCompleteDTO
from .inference import InferenceCoreDTO, InferenceCompleteDTO
from .record_inference import (
    RecordInferenceDTO,
    InferenceRecordDTO,
    RecordAndInferenceDTO,
)

# Rebuild Record
RecordCoreDTO.model_rebuild()
RecordCompleteDTO.model_rebuild()

# Rebuild Inference
InferenceCoreDTO.model_rebuild()
InferenceCompleteDTO.model_rebuild()

# Rebuild Record-Inference
RecordInferenceDTO.model_rebuild()
InferenceRecordDTO.model_rebuild()
RecordAndInferenceDTO.model_rebuild()
