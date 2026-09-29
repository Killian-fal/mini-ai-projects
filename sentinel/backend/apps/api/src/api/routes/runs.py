from fastapi import APIRouter

from api.mappers.runs import runs
from api.schema import Runs
from api.services import runs as service

router = APIRouter()


@router.get("/runs")
def list_runs() -> Runs:
    return runs(*service.listed())
