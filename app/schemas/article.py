from pydantic import BaseModel

class ArticleGenerateIn(BaseModel):
    keyword: str
    style: str
    site_id: int

class ArticleOut(BaseModel):
    title: str
    content: str

class ArticlePublishIn(BaseModel):
    site_id: int
    keyword: str
    title_override: str
    content_override: str
    with_image: bool
