from pydantic import BaseModel, HttpUrl

class SiteCreate(BaseModel):
    wp_url: HttpUrl
    wp_user: str
    wp_app_pass_enc: str
    style: str | None = None
    site_name: str | None = None

class SiteOut(BaseModel):
    id: int
    wp_url: HttpUrl
    wp_user: str
    style: str | None = None
    site_name: str | None = None

    class Config:
        from_attributes = True
