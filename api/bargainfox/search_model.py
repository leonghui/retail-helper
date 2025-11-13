from pydantic import BaseModel


class BargainFoxSearchParams(BaseModel):
    searchText: str
    sort_by: str


class BargainFoxSearchModel(BaseModel):
    api_url: str = "/product/list"
    category: list[str] = []
    limit: int = 300
    pageNumber: int
    searchParams: BargainFoxSearchParams | dict = {}
    authToken: str | None = None
    isSearchAll: bool = True
    cacheSeconds: int = 0
