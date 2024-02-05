import random
import uuid
from typing import Tuple

import pytest

from backend.postgres import Base, get_db
from backend.models import ReimbursementStatus, Reimbursement, Bank, BankMember, BankAdmin, BankAccount
from sqlalchemy import create_engine
from backend.settings import settings
from sqlalchemy.orm import Session

from fastapi.testclient import TestClient
from backend.main import app
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URI = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"  # pylint: disable=line-too-long

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=30,
    max_overflow=20,
    echo=True,
)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session


def seed_bank() -> Bank:
    return Bank(
        name="Bank of America",
        location="123 Bank St, San Francisco, CA 94105",
    )


def seed_bank_member(bank_id: int) -> BankMember:
    return BankMember(
        bank_id=bank_id,
        first_name="BANK"+str(uuid.uuid4().hex),
        last_name="MEMBER"+str(uuid.uuid4().hex),
        email=str(uuid.uuid4().hex) + "@gmail.com",
        phone=str(uuid.uuid4().hex)[:10],
        address_line_1="123 Main St",
        address_line_2="",
        city="San Francisco",
        state="CA",
        zip="94105",
        country="USA",
    )


def seed_bank_admin(bank_id: int) -> BankAdmin:
    return BankAdmin(
        bank_id=bank_id,
        first_name="BANK"+str(uuid.uuid4().hex),
        last_name="ADMIN"+str(uuid.uuid4().hex),
        email=str(uuid.uuid4().hex) + "@gmail.com",
        phone=str(uuid.uuid4().hex)[:10],
    )


def seed_bank_account(member_id: int, bank_id: int) -> BankAccount:
    return BankAccount(
        bank_member_id=member_id,
        bank_id=bank_id,
    )


def seed_reimbursement(bank_id: int, bank_account_id: int) -> Reimbursement:
    return Reimbursement(
        bank_account_id=bank_account_id,
        bank_id=bank_id,
        amount=random.Random().randint(1, 10000),
        description="Some description",
        status=ReimbursementStatus.PENDING,
    )


def seed_db(db: Session) -> Tuple[Bank, BankMember, BankAdmin, BankAccount, Reimbursement]:
    bank = seed_bank()
    db.add(bank)
    db.flush()

    member = seed_bank_member(bank.id)
    db.add(member)
    db.flush()

    admin = seed_bank_admin(bank.id)
    db.add(admin)
    db.flush()

    account = seed_bank_account(member.id, bank.id)
    db.add(account)
    db.flush()

    reimbursement = seed_reimbursement(bank.id, account.id)
    db.add(reimbursement)
    db.flush()

    db.commit()

    db.refresh(bank)
    db.refresh(member)
    db.refresh(admin)
    db.refresh(account)
    db.refresh(reimbursement)

    return bank, member, admin, account, reimbursement


def test_get_reimbursement(session: Session):
    _, _, _, _, reimbursement = seed_db(session)

    r = client.get(
        f"/reimbursements/{reimbursement.id}",
    )

    assert r.status_code == 200, r.text
    fetched_reimbursement = Reimbursement(**r.json())
    assert fetched_reimbursement.id == reimbursement.id


def test_create_reimbursement(session: Session):
    bank, member, admin, account, _ = seed_db(session)

    r = client.post(
        f"/reimbursements",
        json={
            "bank_id": bank.id,
            "bank_account_id": account.id,
            "amount": 1000,
            "description": "FOO",
        },
    )

    assert r.status_code == 201, r.text

    fetched_reimbursement = Reimbursement.get_one(session, r.json()["id"])

    assert fetched_reimbursement.bank_id == r.json()["bank_id"]
    assert fetched_reimbursement.bank_account_id == r.json()["bank_account_id"]
    assert fetched_reimbursement.amount == r.json()["amount"]
    assert fetched_reimbursement.description == r.json()["description"]
    assert fetched_reimbursement.status == ReimbursementStatus.PENDING.value


def test_list_reimbursement(session: Session):
    bank, member, admin, account, reimbursement = seed_db(session)

    r = client.get(
        f"/reimbursements?bank_id=1234566",
    )

    assert r.status_code == 200, r.text
    assert len(r.json()) == 0

    r = client.get(
        f"/reimbursements?bank_id={bank.id}",
    )

    assert r.status_code == 200, r.text
    assert len(r.json()) == 1

    accounts = []

    for _ in range(3):
        a = seed_bank_account(member.id, bank.id)
        accounts.append(a)

    session.add_all(accounts)
    session.flush()

    accounts.append(account)

    reimbursements = []

    for _ in range(10):
        reimbursement = seed_reimbursement(bank.id, account.id)
        reimbursement.status = random.choice(list(ReimbursementStatus)).value
        reimbursement.bank_account_id = random.choice(accounts).id

        reimbursements.append(reimbursement)
    session.add_all(reimbursements)
    session.commit()
    reimbursements.append(reimbursement)

    r = client.get(
        f"/reimbursements?bank_id={bank.id}&status={ReimbursementStatus.PENDING.value}",
    )

    assert r.status_code == 200, r.text
    assert len(r.json()) == len([r for r in reimbursements if r.status == ReimbursementStatus.PENDING.value])


def test_update_reimbursement(session: Session):
    bank, member, admin, account, reimbursement = seed_db(session)

    r = client.patch(
        f"/reimbursements/{reimbursement.id}",
        json={
            "status": ReimbursementStatus.APPROVED.value,
            "decision_by_id": admin.id,
        },
    )

    assert r.status_code == 200, r.text
    fetched_reimbursement = Reimbursement(**r.json())
    assert fetched_reimbursement.id == reimbursement.id
