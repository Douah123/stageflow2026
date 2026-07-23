from typing import Annotated

from fastapi import Query

SkipParam = Annotated[
    int, Query(ge=0, description="Nombre d'éléments à sauter")
]
LimitParam = Annotated[
    int,
    Query(ge=1, le=100, description="Nombre d'éléments à retourner"),
]