from pydantic import BaseModel
from typing import List

class CountTotalAbsen(BaseModel):
    count: int

class VolumeAbsenDate(BaseModel):
    class DetailVolume(BaseModel):
        tanggal_absen: str
        count: int
    data: List[DetailVolume]