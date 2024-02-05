from datetime import datetime
from enum import Enum

from backend.postgres import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import AbstractConcreteBase


class ReimbursementStatus(str, Enum):
    """
    Represents the status of a reimbursement.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Bank(Base):
    """
    Represents a bank as an entity.
    """

    __tablename__ = "bank"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

    name: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()


class BankResource(AbstractConcreteBase, Base):
    strict_attrs = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

    @declared_attr
    def bank_id(cls):
        return mapped_column(ForeignKey('bank.id'))

    @declared_attr
    def bank(cls):
        return relationship("Bank")


class BankAdmin(BankResource):
    __tablename__ = "bank_admin"

    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()


class BankAccount(BankResource):
    __tablename__ = "bank_account"

    bank_member_id: Mapped[int] = mapped_column(ForeignKey('bank_member.id'))
    bank_member: Mapped["BankMember"] = relationship(back_populates="bank_accounts")

    reimbursements: Mapped[list["Reimbursement"]] = relationship(back_populates="bank_account", uselist=True)


class BankMember(BankResource):
    __tablename__ = "bank_member"

    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    address_line_1: Mapped[str] = mapped_column()
    address_line_2: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    zip: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()

    bank_accounts: Mapped[list[BankAccount]] = relationship(back_populates="bank_member", uselist=True)


class Reimbursement(BankResource):
    __tablename__ = "reimbursement"

    bank_account_id: Mapped[int] = mapped_column(ForeignKey('bank_account.id'))
    bank_account: Mapped["BankAccount"] = relationship(back_populates="reimbursements")

    status: Mapped[str] = mapped_column(default=ReimbursementStatus.PENDING.value)
    amount: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column()
    decision_made_at: Mapped[datetime | None] = mapped_column()
    decision_by_id: Mapped[int | None] = mapped_column(ForeignKey('bank_admin.id'))
    notification_sent_at: Mapped[datetime | None] = mapped_column()

    decision_by: Mapped["BankAdmin"] = relationship("BankAdmin")


Base.registry.configure()
