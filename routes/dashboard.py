from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from common.security import oauth2_scheme, get_user_from_jwt_token
from models import get_db_sync
from repository import dashboard as dashboard_repo
from common.responses import (
    common_response,
    Ok,
    InternalServerError,
    Unauthorized
)
from schemas.dashboard import (
    CountTotalAbsen,
    VolumeAbsenDate
)
from schemas.common import (
    BadRequestResponse,
    UnauthorizedResponse,
    ForbiddenResponse,
    InternalServerErrorResponse
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
MSG_UNAUTHORIZED="Invalid/Expire Credentials"

@router.get(
    "/admin/count-day",
    responses={
        "200": {"model": CountTotalAbsen},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def count_admin_day(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
        data = dashboard_repo.count_day_admin(
            db=db,
            start_date=start_date,
            end_date=end_date
        )
        return common_response(
            Ok(
                data={
                    "count": data
                }
            )
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return common_response(InternalServerError(error=str(e)))

@router.get(
    "/user/count-day",
    responses={
        "200": {"model": CountTotalAbsen},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def count_user_day(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
        data = dashboard_repo.count_day_user(
            db=db,
            user=user,
            start_date=start_date,
            end_date=end_date
        )
        return common_response(
            Ok(
                data={
                    "count": data,
                }
            )
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return common_response(InternalServerError(error=str(e)))

@router.get(
    "/admin/volume-month",
    responses={
        "200": {"model": VolumeAbsenDate},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def volume_month_admin(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
        data = dashboard_repo.volume_by_month_admin(
            db=db,
            start_date=start_date,
            end_date=end_date
        )
        return common_response(
            Ok(
                data={
                    "data": [
                        {
                            "tanggal_absen": str(val.tanggal_absen),
                            "count": val.count
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
    "/user/volume-month",
    responses={
        "200": {"model": VolumeAbsenDate},
        "400": {"model": BadRequestResponse},
        "401": {"model": UnauthorizedResponse},
        "403": {"model": ForbiddenResponse},
        "500": {"model": InternalServerErrorResponse},
    }
)
async def volume_month_user(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db_sync),
    token: str = Depends(oauth2_scheme)
):
    try:
        user = get_user_from_jwt_token(db, token)
        if user is None:
            return common_response(Unauthorized(custom_response=MSG_UNAUTHORIZED))
        data = dashboard_repo.volume_by_month_user(
            user=user,
            db=db,
            start_date=start_date,
            end_date=end_date
        )
        for x in data:
            print(x)
        return common_response(
            Ok(
                data={
                    "data": [
                        {
                            "tanggal_absen": str(val.tanggal_absen),
                            "count": val.count
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