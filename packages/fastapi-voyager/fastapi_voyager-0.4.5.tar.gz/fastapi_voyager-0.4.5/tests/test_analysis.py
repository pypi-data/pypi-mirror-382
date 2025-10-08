from fastapi_voyager.graph import Analytics
from pydantic import BaseModel
from fastapi import FastAPI
from typing import Optional


def test_analysis():

    class B(BaseModel):
        id: int
        value: str

    class A(BaseModel):
        id: int
        name: str
        b: B
    
    class C(BaseModel):
        id: int
        name: str
        b: B

    app = FastAPI()

    @app.get("/test", response_model=Optional[A])
    def home():
        return None

    @app.get("/test2", response_model=Optional[C])
    def home2():
        return None

    analytics = Analytics()
    analytics.analysis(app)
    assert len(analytics.nodes) == 3
    assert len(analytics.links) == 6