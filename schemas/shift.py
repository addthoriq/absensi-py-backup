from typing import List, Optional
from pydantic import BaseModel


class PaginateShiftResponse(BaseModel):
    counts: int
    page_count: int
    page_size: int
    page: int

    class DetailShiftResponse(BaseModel):
        id: int
        nama_shift: str
        jam_mulai: str
        jam_akhir: str

    result: List[DetailShiftResponse]


class DetailShiftResponse(BaseModel):
    id: int
    nama_shift: str
    jam_mulai: str
    jam_akhir: str

    class UserList(BaseModel):
        id: int
        email: str
        nama_user: str

        class DetailJabatan(BaseModel):
            id: int
            nama_jabatan: str

        jabatan: Optional[DetailJabatan]
    users: List[UserList]


class CreateShiftRequest(BaseModel):
    nama_shift: str
    jam_mulai: str
    jam_akhir: str


class CreateShiftResponse(BaseModel):
    id: int
    nama_shift: str
    jam_mulai: str
    jam_akhir: str


class UpdateShiftRequest(BaseModel):
    nama_shift: str
    jam_mulai: str
    jam_akhir: str


class UpdateShiftResponse(BaseModel):
    id: int
    nama_shift: str
    jam_mulai: str
    jam_akhir: str

class AssignShiftUserRequest(BaseModel):
    user_id: List[int]

class AssignShiftUserResponse(BaseModel):
    id: int
    nama_shift: str
    jam_mulai: str
    jam_akhir: str
    class UserList(BaseModel):
        id: int
        email: str
        nama: str

        class DetailJabatan(BaseModel):
            id: int
            nama_jabatan: str

        jabatan: Optional[DetailJabatan]
    users: List[UserList]
