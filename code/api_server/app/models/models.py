from pydantic import BaseModel, ConfigDict, Field


class AnnotateBatchArticleRequest(BaseModel):
    """Request model for batch article annotation."""
    url_list: list[str] = Field(..., min_length=1, description="Input text to annotate")

    model_config = ConfigDict(
        extra="forbid",
    )


class AnnotateSingleArticleRequest(BaseModel):
    """Request model for single article annotation. ALSO WORKS FOR RSS."""
    url: str = Field(..., min_length=1, description="Input text to annotate")

    model_config = ConfigDict(
        extra="forbid",
    )


class AnnotateResponse(BaseModel):
    text: str
    annotations: list[dict] = Field(default_factory=list)