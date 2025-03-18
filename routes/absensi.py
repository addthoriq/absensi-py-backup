from typing import Optional
from datetime import datetime, timedelta
from math import radians, sin, cos, asin, sqrt
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from common.security import oauth2_scheme, get_user_from_jwt_token
from models import get_db_sync
from models.User import User
from models.Shift import Shift
from repository import (
    absensi as absensi_repo,
    shift as shift_repo
)
from common.responses import (
    common_response,
    Ok,
    BadRequest,
    NotFound,
    InternalServerError,
    Unauthorized
)
from schemas.absensi import (
    CheckKoordinatRequest,
    DetailAbsensiResponse,
    PaginateAbsensiAdminResponse,
    PaginateAbsensiUserResponse,
    CreateAbsensiMasukRequest,
    CreateAbsensiMasukResponse,
    CreateAbsensiKeluarRequest,
    CreateAbsensiKeluarResponse,
    CheckShift
)
from schemas.common import (
    BadRequestResponse,
    UnauthorizedResponse,
    ForbiddenResponse,
    InternalServerErrorResponse
)
from settings import (
    LONG_OF_CENTER,
    LAT_OF_CENTER,
    CHECK_KILOMETER_RADIUS,
    MIN_MINUTE_ABSEN_IN,
    MAX_MINUTE_ABSEN_IN
)

router = APIRouter(prefix="/absensi", tags=["Absensi"])
MSG_UNAUTHORIZED="Invalid/Expire Credentials"

@router.get(
    "/",
    responses={
        "200": {"model": PaginateAbsensiUserResponse},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def laporan_absensi_by_user(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    jam_masuk: Optional[str] = None,
    jam_keluar: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
        (data, num_data, num_page) = absensi_repo.paginate_list_only_user(
            user=user,
            db=db,
            page=page,
            page_size=page_size,
            start_date=start_date,
            end_date=end_date,
            jam_masuk=jam_masuk,
            jam_keluar=jam_keluar
        )
        return common_response(
            Ok(
                data={
                    "count": num_data,
                    "page_count": num_page,
                    "page_size": page_size,
                    "page": page,
                    "results": [
                        {
                            "id": val.id,
                            "tanggal_absen": str(val.tanggal_absen),
                            "jam_masuk": str(val.jam_masuk),
                            "jam_keluar": str(val.jam_keluar ) if val.jam_keluar else None,
                            "lokasi_masuk": val.lokasi_masuk,
                            "lokasi_keluar": val.lokasi_keluar if val.lokasi_keluar else None,
                            "keterangan": val.keterangan,
                            # "shift": {
                            #     "id": val.absen_shift.id,
                            #     "nama_shift": val.absen_shift.nama_shift,
                            #     "jam_mulai": str(val.absen_shift.jam_mulai),
                            #     "jam_akhir": str(val.absen_shift.jam_akhir)
                            # } if val.absen_shift else None,
                            # "kehadiran": {
                            #     "id": val.absen_kehadiran.id,
                            #     "nama_kehadiran": val.absen_kehadiran.nama_kehadiran,
                            #     "keterangan": val.absen_kehadiran.keterangan,
                            # } if val.absen_kehadiran else None,
                        }
                        for val in data
                    ]
                }
            )
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return common_response(InternalServerError(error=str(e)))

@router.get(
    "/laporan",
    responses={
        "200": {"model": PaginateAbsensiAdminResponse},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def laporan_absensi_only_admin(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    jam_masuk: Optional[str] = None,
    jam_keluar: Optional[str] = None,
    user_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
        (data, num_data, num_page) = absensi_repo.paginate_list_admin(
            db=db,
            page=page,
            page_size=page_size,
            start_date=start_date,
            end_date=end_date,
            user_name=user_name,
            jam_masuk=jam_masuk,
            jam_keluar=jam_keluar
        )
        return common_response(
            Ok(
                data={
                    "count": num_data,
                    "page_count": num_page,
                    "page_size": page_size,
                    "page": page,
                    "results": [
                        {
                            "id": val.id,
                            "tanggal_absen": str(val.tanggal_absen),
                            "jam_masuk": str(val.jam_masuk),
                            "jam_keluar": str(val.jam_keluar ) if val.jam_keluar else None,
                            "keterangan": val.keterangan,
                            "user":{
                                "id": val.absen_user.id,
                                "nama_user": val.absen_user.nama,
                                "email": val.absen_user.email,
                                "jabatan": {
                                    "id": val.absen_user.userRole.id,
                                    "nama_jabatan": val.absen_user.userRole.jabatan
                                } if val.absen_user.userRole else None,
                                "shift": [
                                    {
                                    "id": xal.id,
                                    "nama_shift": xal.nama_shift,
                                    "jam_mulai": str(xal.jam_mulai),
                                    "jam_akhir": str(xal.jam_akhir)
                                    } for xal in val.absen_user.userShift
                                ]if val.absen_user.userShift else None
                            } if val.absen_user else None
                        }
                        for val in data
                    ]
                }
            )
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return common_response(InternalServerError(error=str(e)))

@router.get(
    "/laporan/{id}/",
    responses={
        "200": {"model": DetailAbsensiResponse},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def detail_absen(
    id: str,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
        data = absensi_repo.get_by_id(db, id)
        if data is None:
            return common_response(NotFound())
        return common_response(
            Ok(
                data={
                    "id": data.id,
                    "tanggal_absen": str(data.tanggal_absen),
                    "jam_masuk": str(data.jam_masuk),
                    "jam_keluar": str(data.jam_keluar) if data.jam_keluar else None,
                    "keterangan": data.keterangan,
                    "lokasi_masuk": data.lokasi_masuk,
                    "lokasi_keluar": data.lokasi_keluar if data.lokasi_keluar else None,
                    "user": {
                        "id": data.absen_user.id,
                        "nama_user": data.absen_user.nama,
                        "email": data.absen_user.email,
                        "jabatan": {
                            "id": data.absen_user.userRole.id,
                            "nama_jabatan": data.absen_user.userRole.jabatan
                        } if data.absen_user.userRole else None,
                        "shift": [
                            {
                                "id": val.id,
                                "nama_shift": val.nama_shift,
                                "jam_mulai": str(val.jam_mulai),
                                "jam_akhir": str(val.jam_akhir)
                            }
                            for val in data.absen_user.userShift
                        ] if data.absen_user.userShift else []
                    } if data.absen_user else None
                }
            )
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return common_response(InternalServerError(error=str(e)))

@router.post(
    "/masuk",
    responses={
        "200": {"model": CreateAbsensiMasukResponse},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def absen_masuk(
    req: CreateAbsensiMasukRequest,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))

        check_tanggal_checkout = absensi_repo.get_date_gt_today(db=db, user=user)
        if check_tanggal_checkout is not None:
            absensi_repo.forced_absen_gt_today(db=db, id=check_tanggal_checkout.id)
            return common_response(BadRequest(custom_response={"message": "Maaf, Absensi anda lebih dari sehari. Harap ulang check-in anda lagi!"}))

        check_jam_keluar = absensi_repo.get_absen_without_jam_keluar(db=db, user=user)
        if check_jam_keluar is not None:
            return common_response(BadRequest(custom_response={"message": "Anda belum melakukan Check-Out!"}))

        # jam_sekarang = datetime.now().time()
        # shift, can_check_in, _ = check_shift(db=db, user=user)

        # if not can_check_in:
        #     return common_response(BadRequest(custom_response={"message": "Anda belum bisa Absen Masuk sekarang"}))

        data = absensi_repo.create_masuk(
            db=db,
            keterangan=req.keterangan,
            userId=user,
            lokasi_masuk=req.lokasi_masuk,
            # shift=shift
        )

        return common_response(
            Ok(
                data={
                    "id": data.id,
                    "tanggal_absen": str(data.tanggal_absen),
                    "jam_masuk": str(data.jam_masuk),
                    "keterangan": data.keterangan if data.keterangan is not None else data.keterangan,
                    "lokasi_masuk": data.lokasi_masuk,
                    "user": {
                        "id": data.absen_user.id,
                        "nama_user": data.absen_user.nama,
                        "email": data.absen_user.email,
                        "jabatan": {
                            "id": data.absen_user.userRole.id,
                            "nama_jabatan": data.absen_user.userRole.jabatan
                        } if data.absen_user.userRole else None,
                        "shift": [
                            {
                                "id": val.id,
                                "nama_shift": val.nama_shift,
                                "jam_mulai": str(val.jam_mulai),
                                "jam_akhir": str(val.jam_akhir),
                            }
                            for val in data.absen_user.userShift
                        ]
                        if data.absen_user.userShift else []
                    },
                }
            )
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return common_response(InternalServerError(error=str(e)))

def check_shift(db: Session, user: User):
        shift = get_active_shift(db, user)

        # if not shift:
        #     return {"can_check_in": False, "can_check_out": False, "shift_id": None}

        now = datetime.now()
        today = now.date()
        shift_start = datetime.combine(today, shift.jam_mulai)
        shift_end = datetime.combine(today, shift.jam_akhir)

        can_check_in = shift_start - timedelta(minutes=MIN_MINUTE_ABSEN_IN) <= now <= shift_start
        data = absensi_repo.get_absen_by_user_shift(db=db, user=user, shift=shift)
        can_check_out = shift_end + timedelta(minutes=MAX_MINUTE_ABSEN_IN) <= now <= shift_end and (not data or not data.jam_keluar)
        return shift, can_check_in, can_check_out

@router.get(
    "/check-shift",
    responses={
        "200": {"model": CheckShift},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def check_absen_shift(
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))

        """
        Endpoint untuk mengecek apakah user bisa melakukan check-in atau check-out.
        """
        shift = get_active_shift(db, user)

        if not shift:
            return BadRequest(custom_response={"message": "Shift sudah berakhir"})

        now = datetime.now()
        today = now.date()
        shift_start = datetime.combine(today, shift.jam_mulai)
        shift_end = datetime.combine(today, shift.jam_akhir)

        can_check_in = shift_start - timedelta(minutes=MIN_MINUTE_ABSEN_IN) <= now <= shift_start
        data = absensi_repo.get_absen_by_user_shift(db=db, user=user, shift=shift)
        can_check_out = shift_end + timedelta(minutes=MAX_MINUTE_ABSEN_IN) >= now >= shift_end and (not data or not data.jam_keluar)

        return common_response(
            Ok(
                data={
                    "shift": {
                        "id": shift.id,
                        "nama_shift": shift.nama_shift,
                        "jam_mulai": str(shift.jam_mulai),
                        "jam_akhir": str(shift.jam_akhir),
                    },
                    "bisa_absen_masuk": can_check_in,
                    "bisa_absen_keluar": can_check_out
                }
            )
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return common_response(InternalServerError(error=str(e)))


def get_active_shift(db: Session, user: User) -> Optional[Shift]:
    """
    Mencari shift yang sedang aktif berdasarkan waktu saat ini.
    """
    now = datetime.now()
    today = now.date()

    shifts = shift_repo.get_shift_by_user(db=db, user=user)

    for shift in shifts:
        shift_start = datetime.combine(today, shift.jam_mulai)
        shift_end = datetime.combine(today, shift.jam_akhir)

        if shift_start - timedelta(minutes=MIN_MINUTE_ABSEN_IN) <= now <= shift_end + timedelta(minutes=MAX_MINUTE_ABSEN_IN):
            return shift

    return None  # Tidak ada shift yang valid

@router.post(
    "/check-koordinat",
    responses={
        "200": {"model": bool},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def check_koordinat(
    # req:
    req: CheckKoordinatRequest,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))

        check_radius = haversine(LONG_OF_CENTER, LAT_OF_CENTER, req.longitude, req.latitude)
        area = CHECK_KILOMETER_RADIUS # in kilometer
        if check_radius <= area:
            return common_response(
                Ok(
                    data=True
                )
            )
        else:
            return common_response(
                Ok(
                    data=False
                )
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return common_response(InternalServerError(error=str(e)))

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

@router.put(
    "/keluar/{id}/",
    responses={
        "200": {"model": CreateAbsensiKeluarResponse},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def absen_keluar(
    id: str,
    req: CreateAbsensiKeluarRequest,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
        data = absensi_repo.get_by_id(db, id)
        if data is None:
            return common_response(NotFound())
        # shift, _, can_check_out = check_shift(db=db, user=user)

        # if can_check_out:
        #     return common_response(BadRequest(custom_response={"message": "Anda belum bisa Absen Keluar sekarang"}))

        data = absensi_repo.update_exit(
            db=db,
            id=id,
            # shift=shift,
            lokasi_keluar=req.lokasi_keluar
        )
        return common_response(
            Ok(
                data={
                    "id": data.id,
                    "tanggal_absen": str(data.tanggal_absen),
                    "jam_masuk": str(data.jam_masuk),
                    "jam_keluar": str(data.jam_keluar) if data.jam_keluar else None,
                    "keterangan": data.keterangan if data.keterangan is not None else data.keterangan,
                    "lokasi_masuk": data.lokasi_masuk,
                    "lokasi_keluar": data.lokasi_keluar,
                    "user": {
                        "id": data.absen_user.id,
                        "nama_user": data.absen_user.nama,
                        "email": data.absen_user.email,
                        "jabatan": {
                            "id": data.absen_user.userRole.id,
                            "nama_jabatan": data.absen_user.userRole.jabatan
                        },
                        # "shift": [
                        #     {
                        #         "id": val.id,
                        #         "nama_shift": val.nama_shift,
                        #         "jam_mulai": str(val.jam_mulai),
                        #         "jam_akhir": str(val.jam_akhir),
                        #     }
                        #     for val in data.absen_user.userShift
                        # ]
                        # if data.absen_user.userShift else []
                    }
                }
            )
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return common_response(InternalServerError(error=str(e)))

# @router.get(
#     "/download-excel/admin",
# )
# async def download_rekap_absen_admin(
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     jam_masuk: Optional[str] = None,
#     jam_keluar: Optional[str] = None,
#     user_name: Optional[str] = None,
#     db: Session = Depends(get_db_sync),
#     token: str = Depends(oauth2_scheme)
# ):
#     try:
#         user = get_user_from_jwt_token(db, token)
#         if user is None:
#             return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
#         data = absensi_repo.export_excel_admin(
#             db=db,
#             start_date=start_date,
#             end_date=end_date,
#             jam_masuk=jam_masuk,
#             jam_keluar=jam_keluar,
#             user_name=user_name
#         )
#         if data:
#             df = pl.DataFrame(
#                 {
#                     "Nama": val.absen_user.nama,
#                     "Tanggal Absen": str(val.tanggal_absen),
#                     "Jam Masuk": str(val.jam_masuk),
#                     "Jam Keluar": str(val.jam_keluar ) if val.jam_keluar else None,
#                     "Lokasi Masuk": val.lokasi_masuk,
#                     "Lokasi Keluar": val.lokasi_keluar if val.lokasi_keluar else None,
#                     "Keterangan": val.keterangan,
#                 }
#                 for val in data
#             )
#         else:
#             df = pl.DataFrame(
#                 {
#                     "Tanggal Absen": None,
#                     "Jam Masuk": None,
#                     "Jam Keluar": None,
#                     "Lokasi Masuk": None,
#                     "Lokasi Keluar": None,
#                     "Keterangan": None,
#                 }
#             )

#         buffer = BytesIO()
#         df.write_excel(buffer)
#         buffer.seek(0)
#         nama_file = "Rekap Absensi.xlsx"
#         return StreamingResponse(
#             buffer,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={"Content-Disposition": f"attachment; filename={nama_file}"},
#         )


#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return common_response(InternalServerError(error=str(e)))

# @router.get(
#     "/download-excel/user",
# )
# async def download_rekap_absen_user(
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     jam_masuk: Optional[str] = None,
#     jam_keluar: Optional[str] = None,
#     db: Session = Depends(get_db_sync),
#     token: str = Depends(oauth2_scheme)
# ):
#     try:
#         user = get_user_from_jwt_token(db, token)
#         if user is None:
#             return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
#         data = absensi_repo.export_excel_user(
#             user=user,
#             db=db,
#             start_date=start_date,
#             end_date=end_date,
#             jam_masuk=jam_masuk,
#             jam_keluar=jam_keluar,
#         )
#         if data:
#             df = pl.DataFrame(
#                 {
#                     "Tanggal Absen": str(val.tanggal_absen),
#                     "Jam Masuk": str(val.jam_masuk),
#                     "Jam Keluar": str(val.jam_keluar ) if val.jam_keluar else None,
#                     "Lokasi Masuk": val.lokasi_masuk,
#                     "Lokasi Keluar": val.lokasi_keluar if val.lokasi_keluar else None,
#                     "Keterangan": val.keterangan,
#                 }
#                 for val in data
#             )
#         else:
#             df = pl.DataFrame(
#                 {
#                     "Tanggal Absen": None,
#                     "Jam Masuk": None,
#                     "Jam Keluar": None,
#                     "Lokasi Masuk": None,
#                     "Lokasi Keluar": None,
#                     "Keterangan": None,
#                 }
#             )

#         buffer = BytesIO()
#         df.write_excel(buffer)
#         buffer.seek(0)
#         nama_file = f"Rekap Absensi {user.nama}.xlsx"
#         return StreamingResponse(
#             buffer,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={"Content-Disposition": f"attachment; filename={nama_file}"},
#         )


    # except Exception as e:
    #     import traceback
    #     traceback.print_exc()
    #     return common_response(InternalServerError(error=str(e)))
