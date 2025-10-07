from enum import Enum


class FlightRequestType(str, Enum):
    EVALUATION = "evaluation"
    ANNOTATION = "annotation"
    METADATA = "metadata"
