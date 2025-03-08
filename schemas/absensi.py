from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class PaginateAbsensiUserResponse(BaseModel):
    count: int
    page_count: int
    page_size: int
    page: int
    class DetailAbsensiResponse(BaseModel):
        id: int
        tanggal_absen: date
        jam_masuk: str
        jam_keluar: Optional[str]
        keterangan: str
        lokasi_masuk: str
        lokasi_keluar: Optional[str]
    results: List[DetailAbsensiResponse]

class PaginateAbsensiAdminResponse(BaseModel):
    count: int
    page_count: int
    page_size: int
    page: int

    class DetailAbsensiResponse(BaseModel):
        id: int
        tanggal_absen: date
        jam_masuk: str
        jam_keluar: Optional[str]
        keterangan: str
        lokasi_masuk: str
        lokasi_keluar: Optional[str]

        class GetUserDetail(BaseModel):
            id: int
            nama_user: str
            email: str

            class GetJabatanUser(BaseModel):
                id: int
                nama_jabatan: str

            jabatan: List[GetJabatanUser]

            class GetShiftDetail(BaseModel):
                id: int
                nama_shift: str
                jam_mulai: str
                jam_akhir: str

            shift: List[GetShiftDetail]

        user: List[GetUserDetail]

    results: List[DetailAbsensiResponse]


class DetailAbsensiResponse(BaseModel):
    id: int
    tanggal_absen: date
    jam_masuk: str
    jam_keluar: Optional[str]
    keterangan: str
    lokasi_masuk: str
    lokasi_keluar: Optional[str]

    class GetUserDetail(BaseModel):
        id: int
        nama_user: str
        email: str

        class GetJabatanUser(BaseModel):
            id: int
            nama_jabatan: str

        jabatan: List[GetJabatanUser]

        class GetShiftDetail(BaseModel):
            id: int
            nama_shift: str
            jam_mulai: str
            jam_akhir: str
        shift: List[GetShiftDetail]

    user: List[GetUserDetail]

class CreateAbsensiMasukRequest(BaseModel):
    lokasi_masuk: str
    keterangan: Optional[str] = None

class CheckKoordinatRequest(BaseModel):
    longitude: float
    latitude: float

class CreateAbsensiMasukResponse(BaseModel):
    id: int
    tanggal_absen: date
    jam_masuk: str
    keterangan: str
    lokasi_masuk: str

    class GetUserDetail(BaseModel):
        id: int
        nama_user: str
        email: str

        class GetJabatanUser(BaseModel):
            id: int
            nama_jabatan: str

        jabatan: List[GetJabatanUser]

        class GetShiftDetail(BaseModel):
            id: int
            nama_shift: str
            jam_mulai: str
            jam_akhir: str
        shift: List[GetShiftDetail]

    user: List[GetUserDetail]

class CreateAbsensiKeluarRequest(BaseModel):
    lokasi_keluar: str

class CreateAbsensiKeluarResponse(BaseModel):
    tanggal_absen: date
    jam_masuk: str
    jam_keluar: str
    keterangan: str
    lokasi_masuk: str
    lokasi_keluar: str

    class GetUserDetail(BaseModel):
        id: int
        nama_user: str
        email: str

        class GetJabatanUser(BaseModel):
            id: int
            nama_jabatan: str

        jabatan: List[GetJabatanUser]

        class GetShiftDetail(BaseModel):
            id: int
            nama_shift: str
            jam_mulai: str
            jam_akhir: str

        shift: List[GetShiftDetail]

    user: List[GetUserDetail]
