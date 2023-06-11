from fastapi import FastAPI, APIRouter, Depends
from fastapi_utils.inferring_router import InferringRouter


def create_routes(app: FastAPI, **kwargs):
    app.include_router(router=router)


router = APIRouter(
    prefix='',
    tags=['test_start']
)


# @router.get("/")
async def root():
    return {"message": "Hello World"}


router.get(path='/')(root)


InferringRouter

class BaseView():

    def get(self, *args, **kwargs):
        return router.get(*args, **kwargs)
