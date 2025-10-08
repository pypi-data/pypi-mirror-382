from typing import Type, Optional, List

from pydantic import BaseModel


class CatwalkDataType(BaseModel):
    key: str
    description: str
    example: dict
    json_schema: Optional[dict] = None
    src: str
    main: str


class CatwalkEvaluation(BaseModel):
    key: str
    description: str
    example: dict
    json_schema: Optional[dict] = None
    src: str
    main: str


class BaseDateType(BaseModel):
    name: str


class BaseEvaluation(BaseModel):
    name: str
    question: str


class CatwalkPlugin:
    name: str
    data_types: List[CatwalkDataType]
    evaluations: List[CatwalkEvaluation]

    def __init__(self, name: str):
        self.name = name
        self.data_types = []
        self.evaluations = []

    def declare_data_type(
        self,
        key: str,
        *,
        description: str,
        example: dict,
        src: str,
        main: str,
        model: Type[BaseModel] = None,
    ):
        data_model = type(
            f"DataType{key}", (BaseDateType, model) if model else (BaseDateType,), {}
        )
        self.data_types.append(
            CatwalkDataType(
                key=key,
                description=description,
                example=example,
                src=src,
                main=main,
                json_schema=data_model.schema(),
            )
        )
        return self

    def declare_evaluation(
        self,
        key: str,
        *,
        description: str,
        example: dict,
        src: str,
        main: str,
        model: Type[BaseModel] = None,
    ):
        data_model = type(
            f"Evaluation{key}",
            (BaseEvaluation, model) if model else (BaseEvaluation,),
            {},
        )
        self.evaluations.append(
            CatwalkEvaluation(
                key=key,
                description=description,
                example=example,
                src=src,
                main=main,
                json_schema=data_model.schema(),
            )
        )
        return self

    def dict(self):
        return {
            "name": self.name,
            "data_types": [x.dict() for x in self.data_types],
            "evaluations": [x.dict() for x in self.evaluations],
        }
