from typing import Any, Union, Optional, List

from pydantic import ConfigDict, BaseModel, Field


class Type(BaseModel):
    name: str
    model_config = ConfigDict(extra="allow")


class Evaluation(BaseModel):
    question: str
    name: str
    model_config = ConfigDict(extra="allow")


class EvaluationResult(BaseModel):
    question: str
    value: Any = None
    model_config = ConfigDict(extra="allow")


class Query(BaseModel):
    name: str
    value: Any = None
    type: Union[Type, str]


class Response(BaseModel):
    name: str
    value: Any = None
    type: Union[Type, str]


class Context(BaseModel):
    name: str
    value: Any = None
    type: Union[Type, str]


class Submitter(BaseModel):
    name: str
    version: str


class CommonCaseFormat(BaseModel):
    track_id: Optional[str] = Field(
        None,
        description="Unique identifier given by the user used for identifying specific cases.",
    )
    version: int = Field(1, description="Version of the Common Case Format.")
    submitter: Submitter = Field(..., description="Who is the submitter of the case")
    query: List[Query] = Field(
        ...,
        description="List of query objects that describes what was the input for the case",
    )
    response: List[Response] = Field(
        ..., description="List of response objects that describes what was the response"
    )
    context: Optional[List[Context]] = Field(
        None, description="Context that was available for model"
    )
    metadata: dict = Field(
        ..., description="Additional metadata that will be saved with the case"
    )

    def parse_submitter(self):
        return {
            "submitter_name": self.submitter.name,
            "submitter_version": self.submitter.version,
        }

    def to_df_row(self):
        return {
            "track_id": self.track_id,
            "version": self.version,
            **self.parse_submitter(),
            "query": [q.dict() for q in self.query] if self.query else None,
            "response": [r.dict() for r in self.response] if self.response else None,
            "context": [c.dict() for c in self.context] if self.context else None,
            "metadata": self.metadata,
        }

    @staticmethod
    def df_columns():
        return [
            "track_id",
            "version",
            "submitter_name",
            "submitter_version",
            "query",
            "response",
            "context",
            "metadata",
        ]


class OpenCase(CommonCaseFormat):
    id: str
    created_at: str
    is_archived: Optional[bool] = None
    is_open: Optional[bool] = None

    def to_df_row(self):
        return {
            "id": self.id,
            **super().to_df_row(),
            "created_at": self.created_at,
            "is_archived": self.is_archived,
            "is_open": self.is_open,
        }

    @staticmethod
    def df_columns():
        return [
            "id",
            *CommonCaseFormat.df_columns(),
            "created_at",
            "is_archived",
            "is_open",
        ]
