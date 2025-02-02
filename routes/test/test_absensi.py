from unittest import IsolatedAsyncioTestCase
from freezegun import freeze_time
from models.Absensi import Absensi
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from main import app
from common.security import generate_jwt_token_from_user, generate_hash_password
import alembic.config
from models import factory_session, clear_all_data_on_database
from migrations.factories.UserFactory import UserFactory
from migrations.factories.RoleFactory import RoleFactory
from seeders.shift import list_shift
from seeders.kehadiran import list_kehadiran
from repository import (
    absensi as absensi_repo,
    shift as shift_repo,
    kehadiran as kehadiran_repo
)


class TestAbsensi(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        alembic_args = ["-c", "alembic.ini", "upgrade", "head"]
        alembic.config.main(argv=alembic_args)
        self.db: Session = factory_session()
        clear_all_data_on_database(self.db)
        return super().setUp()

    async def test_paginate_absensi_admin(self):
        # Given
        list_role = [
            RoleFactory.create(jabatan="Admin"),
            RoleFactory.create(jabatan="Operator"),
            RoleFactory.create(jabatan="Guru"),
        ]
        list_users = [
            UserFactory.create(
                email="admin@example.com",
                nama="Admin",
                password=generate_hash_password("12qwaszx"),
                userRole=list_role[0],
            ),
            UserFactory.create(
                email="operator@example.com",
                nama="operator",
                password=generate_hash_password("12qwaszx"),
                userRole=list_role[1],
            ),
            UserFactory.create(
                email="guru@example.com",
                nama="Guru",
                password=generate_hash_password("12qwaszx"),
                userRole=list_role[2],
            ),
        ]
        shift_db = []
        for shift in list_shift:
            shift_db.append(shift_repo.create(
                db=self.db,
                nama_shift=shift["nama_shift"], 
                jam_mulai=shift["jam_mulai"], 
                jam_akhir=shift["jam_akhir"],
                is_commit=False
            ))
        kehadiran_db = []
        for kehadiran in list_kehadiran:
            kehadiran_db.append(kehadiran_repo.create(
                db=self.db,
                nama_kehadiran=kehadiran["nama_kehadiran"], 
                keterangan=kehadiran["keterangan"], 
                is_commit=False
            ))
        list_absen = [
            absensi_repo.create_masuk(
                db=self.db,
                lokasi_masuk="41.40338, 2.17403",
                userId=list_users[2],
                shift_id=shift_db[0].id,
                kehadiran_id=kehadiran_db[1].id,
                keterangan=None,
                is_commit=False
            ),
            absensi_repo.create_masuk(
                db=self.db,
                lokasi_masuk="41.40338, 2.17403",
                userId=list_users[1],
                shift_id=shift_db[1].id,
                kehadiran_id=kehadiran_db[0].id,
                keterangan=None,
                is_commit=False
            ),
        ]
        self.db.commit()
        token = await generate_jwt_token_from_user(list_users[0])
        client = TestClient(app)

        # When
        response = client.get(
            "/absensi/laporan", headers={"Authorization": f"Bearer {token}"}
        )

        # Expect
        self.assertEqual(response.status_code, 200)
        output = {
            "count": 2,
            "page_count": 1,
            "page_size": 10,
            "page": 1,
            "results": [
                {
                    "id": val.id,
                    "tanggal_absen": str(val.tanggal_absen),
                    "jam_masuk": str(val.jam_masuk),
                    "jam_keluar": str(val.jam_keluar ) if val.jam_keluar else None,
                    "keterangan": val.keterangan,
                    "shift": {
                        "id": val.absen_shift.id,
                        "nama_shift": val.absen_shift.nama_shift,
                        "jam_mulai": str(val.absen_shift.jam_mulai),
                        "jam_akhir": str(val.absen_shift.jam_akhir)
                    } if val.absen_shift else None,
                    "kehadiran": {
                        "id": val.absen_kehadiran.id,
                        "nama_kehadiran": val.absen_kehadiran.nama_kehadiran,
                        "keterangan": val.absen_kehadiran.keterangan,
                    } if val.absen_kehadiran else None,
                    "user":{
                        "id": val.absen_user.id,
                        "nama_user": val.absen_user.nama,
                        "email": val.absen_user.email,
                        "jabatan": {
                            "id": val.absen_user.userRole.id,
                            "nama_jabatan": val.absen_user.userRole.jabatan
                        } if val.absen_user.userRole else None
                    } if val.absen_user else None
                }
                for val in list_absen
            ],
        }
        self.maxDiff = None
        self.assertEqual(response.json(), output)

    async def test_paginate_absensi_user(self):
        # Given
        list_role = [
            RoleFactory.create(jabatan="Admin"),
            RoleFactory.create(jabatan="Operator"),
            RoleFactory.create(jabatan="Guru"),
        ]
        list_users = [
            UserFactory.create(
                email="admin@example.com",
                nama="Admin",
                password=generate_hash_password("12qwaszx"),
                userRole=list_role[0],
            ),
            UserFactory.create(
                email="operator@example.com",
                nama="operator",
                password=generate_hash_password("12qwaszx"),
                userRole=list_role[1],
            ),
            UserFactory.create(
                email="guru@example.com",
                nama="Guru",
                password=generate_hash_password("12qwaszx"),
                userRole=list_role[2],
            ),
        ]
        shift_db = []
        for shift in list_shift:
            shift_db.append(shift_repo.create(
                db=self.db,
                nama_shift=shift["nama_shift"], 
                jam_mulai=shift["jam_mulai"], 
                jam_akhir=shift["jam_akhir"],
                is_commit=False
            ))
        kehadiran_db = []
        for kehadiran in list_kehadiran:
            kehadiran_db.append(kehadiran_repo.create(
                db=self.db,
                nama_kehadiran=kehadiran["nama_kehadiran"], 
                keterangan=kehadiran["keterangan"], 
                is_commit=False
            ))

        absensi_repo.create_masuk(
            db=self.db,
            lokasi_masuk="41.40338, 2.17403",
            userId=list_users[1],
            shift_id=shift_db[0].id,
            kehadiran_id=kehadiran_db[1].id,
            keterangan=None,
            is_commit=False
        )
        list_absen = [
            absensi_repo.create_masuk(
                db=self.db,
                lokasi_masuk="41.40338, 2.17403",
                userId=list_users[2],
                shift_id=shift_db[0].id,
                kehadiran_id=kehadiran_db[0].id,
                keterangan=None,
                is_commit=False
            ),
            absensi_repo.create_masuk(
                db=self.db,
                lokasi_masuk="41.40338, 2.17403",
                userId=list_users[2],
                shift_id=shift_db[1].id,
                kehadiran_id=kehadiran_db[0].id,
                keterangan=None,
                is_commit=False
            ),
        ]
        self.db.commit()
        token = await generate_jwt_token_from_user(list_users[2])
        client = TestClient(app)

        # When
        response = client.get(
            "/absensi", headers={"Authorization": f"Bearer {token}"}
        )

        # Expect
        self.assertEqual(response.status_code, 200)
        output = {
            "count": 2,
            "page_count": 1,
            "page_size": 10,
            "page": 1,
            "results": [
                {
                    "id": val.id,
                    "tanggal_absen": str(val.tanggal_absen),
                    "jam_masuk": str(val.jam_masuk),
                    "jam_keluar": str(val.jam_keluar ) if val.jam_keluar else None,
                    "keterangan": val.keterangan,
                    "shift": {
                        "id": val.absen_shift.id,
                        "nama_shift": val.absen_shift.nama_shift,
                        "jam_mulai": str(val.absen_shift.jam_mulai),
                        "jam_akhir": str(val.absen_shift.jam_akhir)
                    } if val.absen_shift else None,
                    "kehadiran": {
                        "id": val.absen_kehadiran.id,
                        "nama_kehadiran": val.absen_kehadiran.nama_kehadiran,
                        "keterangan": val.absen_kehadiran.keterangan,
                    } if val.absen_kehadiran else None,
                }
                for val in list_absen
            ],
        }
        self.maxDiff = None
        self.assertEqual(response.json(), output)

    async def test_detail_absensi(self):
        data_role = RoleFactory.create(jabatan="Guru")
        data_user = UserFactory.create(
            email="guru@example.com",
            nama="Guru",
            password=generate_hash_password("12qwaszx"),
            userRole=data_role,
        )
        shift_db = []
        for shift in list_shift:
            shift_db.append(shift_repo.create(
                db=self.db,
                nama_shift=shift["nama_shift"], 
                jam_mulai=shift["jam_mulai"], 
                jam_akhir=shift["jam_akhir"],
                is_commit=False
            ))
        kehadiran_db = []
        for kehadiran in list_kehadiran:
            kehadiran_db.append(kehadiran_repo.create(
                db=self.db,
                nama_kehadiran=kehadiran["nama_kehadiran"], 
                keterangan=kehadiran["keterangan"], 
                is_commit=False
            ))
        data = absensi_repo.create_masuk(
            db=self.db,
            lokasi_masuk="41.40338, 2.17403",
            userId=data_user,
            shift_id=shift_db[0].id,
            kehadiran_id=kehadiran_db[1].id,
            keterangan=None,
            is_commit=False
        )
        self.db.commit()
        token = await generate_jwt_token_from_user(data_user)
        client = TestClient(app)

        # When
        response = client.get(
            f"/absensi/laporan/{data.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Expect
        self.assertEqual(response.status_code, 200)
        output = {
            "id": data.id,
            "tanggal_absen": str(data.tanggal_absen),
            "jam_masuk": str(data.jam_masuk),
            "jam_keluar": str(data.jam_keluar) if data.jam_keluar else None,
            "keterangan": data.keterangan,
            "lokasi_masuk": data.lokasi_masuk,
            "lokasi_keluar": data.lokasi_keluar if data.lokasi_keluar else None,
            "shift": {
                "id": data.absen_shift.id,
                "nama_shift": data.absen_shift.nama_shift,
                "jam_mulai": data.absen_shift.jam_mulai,
                "jam_akhir": data.absen_shift.jam_akhir,
            } if data.absen_shift else None,
            "kehadiran": {
                "id": data.absen_kehadiran.id,
                "nama_kehadiran": data.absen_kehadiran.nama_kehadiran,
                "keterangan": data.absen_kehadiran.keterangan
            } if data.absen_kehadiran else None,
            "user": {
                "id": data.absen_user.id,
                "nama_user": data.absen_user.nama,
                "email": data.absen_user.email,
                "jabatan": {
                    "id": data.absen_user.userRole.id,
                    "nama_jabatan": data.absen_user.userRole.jabatan
                } if data.absen_user.userRole else None
            } if data.absen_user else None
        }
        self.maxDiff = None
        self.assertEqual(response.json(), output)

    async def test_detail_absensi_not_found(self):
        data_role = RoleFactory.create(jabatan="Guru")
        data_user = UserFactory.create(
            email="guru@example.com",
            nama="Guru",
            password=generate_hash_password("12qwaszx"),
            userRole=data_role,
        )
        self.db.commit()
        token = await generate_jwt_token_from_user(data_user)
        client = TestClient(app)

        # When
        response = client.get(
            "/absensi/laporan/2001",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Expect
        self.assertEqual(response.status_code, 404)

    async def test_create_absensi_masuk(self):
        data_role = RoleFactory.create(jabatan="Guru")
        data_user = UserFactory.create(
            email="guru@example.com",
            nama="Guru",
            password=generate_hash_password("12qwaszx"),
            userRole=data_role,
        )
        shift_db = []
        for shift in list_shift:
            shift_db.append(shift_repo.create(
                db=self.db,
                nama_shift=shift["nama_shift"], 
                jam_mulai=shift["jam_mulai"], 
                jam_akhir=shift["jam_akhir"],
                is_commit=False
            ))
        kehadiran_db = []
        for kehadiran in list_kehadiran:
            kehadiran_db.append(kehadiran_repo.create(
                db=self.db,
                nama_kehadiran=kehadiran["nama_kehadiran"], 
                keterangan=kehadiran["keterangan"], 
                is_commit=False
            ))
        self.db.commit()
        token = await generate_jwt_token_from_user(data_user)
        client = TestClient(app)
        req = {
            "lokasi_masuk": "41.40338, 2.17403",
            "keterangan": None,
            "shift_id": shift_db[0].id,
            "kehadiran_id": kehadiran_db[0].id,
        }

        # When
        response = client.post(
            "/absensi/masuk",
            headers={"Authorization": f"Bearer {token}"},
            json=req
        )

        # Expect
        self.assertEqual(response.status_code, 200)
        result = response.json()
        output = {
            "id": result["id"],
            "tanggal_absen": result["tanggal_absen"],
            "jam_masuk": result["jam_masuk"],
            "keterangan": req["keterangan"],
            "lokasi_masuk": req["lokasi_masuk"],
            "shift": {
                "id": shift_db[0].id,
                "nama_shift": shift_db[0].nama_shift,
                "jam_mulai": str(shift_db[0].jam_mulai),
                "jam_akhir": str(shift_db[0].jam_akhir),
            } if shift_db[0] else None,
            "kehadiran": {
                "id": kehadiran_db[0].id,
                "nama_kehadiran": kehadiran_db[0].nama_kehadiran,
                "keterangan": kehadiran_db[0].keterangan
            } if kehadiran_db[0] else None,
            "user": {
                "id": data_user.id,
                "nama_user": data_user.nama,
                "email": data_user.email,
                "jabatan": {
                    "id": data_user.userRole.id,
                    "nama_jabatan": data_user.userRole.jabatan
                } if data_user.userRole else None
            } if data_user else None
        }
        self.maxDiff = None
        self.assertEqual(response.json(), output)
        check_db = (
            self.db.query(Absensi)
            .filter(
                Absensi.id == result["id"],
                Absensi.lokasi_masuk == req["lokasi_masuk"],
                Absensi.shift_id == req["shift_id"],
                Absensi.kehadiran_id == req["kehadiran_id"],
            )
            .first()
        )
        self.assertIsNotNone(check_db)

    # Negatif Case
    async def test_create_absensi_masuk_gt_today(self):
        data_role = RoleFactory.create(jabatan="Guru")
        data_user = UserFactory.create(
            email="guru@example.com",
            nama="Guru",
            password=generate_hash_password("12qwaszx"),
            userRole=data_role,
        )
        shift_db = []
        for shift in list_shift:
            shift_db.append(shift_repo.create(
                db=self.db,
                nama_shift=shift["nama_shift"], 
                jam_mulai=shift["jam_mulai"], 
                jam_akhir=shift["jam_akhir"],
                is_commit=False
            ))
        kehadiran_db = []
        for kehadiran in list_kehadiran:
            kehadiran_db.append(kehadiran_repo.create(
                db=self.db,
                nama_kehadiran=kehadiran["nama_kehadiran"], 
                keterangan=kehadiran["keterangan"], 
                is_commit=False
            ))
        with freeze_time("2024-12-28"):
            absensi_repo.create_masuk(
                db=self.db,
                lokasi_masuk="41.40338, 2.17403",
                userId=data_user,
                shift_id=shift_db[0].id,
                kehadiran_id=kehadiran_db[1].id,
                keterangan=None,
                is_commit=False
            )
        self.db.commit()
        token = await generate_jwt_token_from_user(data_user)
        client = TestClient(app)
        req = {
            "lokasi_masuk": "41.40338, 2.17403",
            "keterangan": None,
            "shift_id": shift_db[0].id,
            "kehadiran_id": kehadiran_db[0].id,
        }

        # When
        response = client.post(
            "/absensi/masuk",
            headers={"Authorization": f"Bearer {token}"},
            json=req
        )

        # Expect
        self.assertEqual(response.status_code, 400)
        output = {"message": "Maaf, Absensi anda lebih dari sehari. Harap ulang check-in anda lagi!"}
        self.maxDiff = None
        self.assertEqual(response.json(), output)
        check_db = (
            self.db.query(Absensi)
            .filter(
                Absensi.lokasi_masuk == req["lokasi_masuk"],
                Absensi.shift_id == req["shift_id"],
                Absensi.kehadiran_id == req["kehadiran_id"],
            )
            .first()
        )
        self.assertIsNone(check_db)

    # Negatif Case
    async def test_create_absensi_masuk_without_jam_keluar(self):
        data_role = RoleFactory.create(jabatan="Guru")
        data_user = UserFactory.create(
            email="guru@example.com",
            nama="Guru",
            password=generate_hash_password("12qwaszx"),
            userRole=data_role,
        )
        shift_db = []
        for shift in list_shift:
            shift_db.append(shift_repo.create(
                db=self.db,
                nama_shift=shift["nama_shift"], 
                jam_mulai=shift["jam_mulai"], 
                jam_akhir=shift["jam_akhir"],
                is_commit=False
            ))
        kehadiran_db = []
        for kehadiran in list_kehadiran:
            kehadiran_db.append(kehadiran_repo.create(
                db=self.db,
                nama_kehadiran=kehadiran["nama_kehadiran"], 
                keterangan=kehadiran["keterangan"], 
                is_commit=False
            ))
        with freeze_time("2024-12-28 07:00:00"):
            absensi_repo.create_masuk(
                db=self.db,
                lokasi_masuk="41.40338, 2.17403",
                userId=data_user,
                shift_id=shift_db[0].id,
                kehadiran_id=kehadiran_db[1].id,
                keterangan=None,
                is_commit=False
            )
        self.db.commit()
        token = await generate_jwt_token_from_user(data_user)
        client = TestClient(app)
        req = {
            "lokasi_masuk": "41.40338, 2.17403",
            "keterangan": None,
            "shift_id": shift_db[0].id,
            "kehadiran_id": kehadiran_db[0].id,
        }

        # When
        with freeze_time("2024-12-28 20:00:00"):
            response = client.post(
                "/absensi/masuk",
                headers={"Authorization": f"Bearer {token}"},
                json=req
            )

        # Expect
        self.assertEqual(response.status_code, 400)
        output = {"message": "Anda belum melakukan Check-Out!"}
        self.maxDiff = None
        self.assertEqual(response.json(), output)
        check_db = (
            self.db.query(Absensi)
            .filter(
                Absensi.lokasi_masuk == req["lokasi_masuk"],
                Absensi.shift_id == req["shift_id"],
                Absensi.kehadiran_id == req["kehadiran_id"],
            )
            .first()
        )
        self.assertIsNone(check_db)

    async def test_update_absensi_keluar(self):
        data_role = RoleFactory.create(jabatan="Guru")
        data_user = UserFactory.create(
            email="guru@example.com",
            nama="Guru",
            password=generate_hash_password("12qwaszx"),
            userRole=data_role,
        )
        shift_db = []
        for shift in list_shift:
            shift_db.append(shift_repo.create(
                db=self.db,
                nama_shift=shift["nama_shift"], 
                jam_mulai=shift["jam_mulai"], 
                jam_akhir=shift["jam_akhir"],
                is_commit=False
            ))
        kehadiran_db = []
        for kehadiran in list_kehadiran:
            kehadiran_db.append(kehadiran_repo.create(
                db=self.db,
                nama_kehadiran=kehadiran["nama_kehadiran"], 
                keterangan=kehadiran["keterangan"], 
                is_commit=False
            ))
        self.db.commit()
        data_absen = absensi_repo.create_masuk(
            db=self.db,
            lokasi_masuk="41.40338, 2.17403",
            userId=data_user,
            shift_id=shift_db[0].id,
            kehadiran_id=kehadiran_db[0].id,
            keterangan=None,
            is_commit=True
        )
        token = await generate_jwt_token_from_user(data_user)
        client = TestClient(app)
        req = {
            "lokasi_keluar": "41.40338, 2.17403",
        }

        # When
        response = client.put(
            f"/absensi/keluar/{data_absen.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=req,
        )

        # Expect
        self.assertEqual(response.status_code, 200)
        result = response.json()
        output = {
            "id": result["id"],
            "tanggal_absen": result["tanggal_absen"],
            "jam_masuk": result["jam_masuk"],
            "jam_keluar": result["jam_keluar"],
            "keterangan": result["keterangan"] if result["keterangan"] is not None else result["keterangan"],
            "lokasi_masuk": result["lokasi_masuk"],
            "lokasi_keluar": req["lokasi_keluar"],
            "shift": {
                "id": shift_db[0].id,
                "nama_shift": shift_db[0].nama_shift,
                "jam_mulai": str(shift_db[0].jam_mulai),
                "jam_akhir": str(shift_db[0].jam_akhir),
            } if shift_db[0] else None,
            "kehadiran": {
                "id": kehadiran_db[0].id,
                "nama_kehadiran": kehadiran_db[0].nama_kehadiran,
                "keterangan": kehadiran_db[0].keterangan
            } if kehadiran_db[0] else None,
            "user": {
                "id": data_user.id,
                "nama_user": data_user.nama,
                "email": data_user.email,
                "jabatan": {
                    "id": data_user.userRole.id,
                    "nama_jabatan": data_user.userRole.jabatan
                } if data_user.userRole else None
            } if data_user else None
        }
        self.maxDiff = None
        self.assertEqual(result, output)
        check_db = (
            self.db.query(Absensi)
            .filter(
                Absensi.id == data_absen.id,
                Absensi.jam_keluar is not None,
                Absensi.lokasi_keluar == req["lokasi_keluar"]
            )
            .first()
        )
        self.assertIsNotNone(check_db)


    def tearDown(self) -> None:
        self.db.rollback()
        factory_session.remove()
        return super().tearDown()
