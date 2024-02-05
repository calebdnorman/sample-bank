from pydantic import BaseModel, Field

from backend.models import ReimbursementStatus, Reimbursement

from datetime import datetime, date
from typing import Annotated, Literal
from sqlalchemy import select, cast, Date
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from backend.postgres import get_db
from fastapi import status as http_status
from fastapi import HTTPException, Depends, BackgroundTasks, Body, Query, Path, APIRouter



class CreateReimbursementRequest(BaseModel):
    bank_account_id: int = Field()
    bank_id: int = Field()
    amount: int = Field()
    description: str = Field()


class UpdateReimbursementRequest(BaseModel):
    status: Literal[ReimbursementStatus.APPROVED, ReimbursementStatus.REJECTED] = Field()
    decision_by_id: int = Field()


class ReimbursementResponse(BaseModel):
    id: int = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
    deleted_at: datetime | None = Field(None)

    bank_account_id: int = Field()
    bank_id: int = Field()
    amount: int = Field()
    description: str = Field()
    status: ReimbursementStatus = Field()
    decision_made_at: datetime | None = Field(None)
    decision_by_id: int | None = Field(None)
    notification_sent_at: datetime | None = Field(None)


router = APIRouter()


@router.post("/reimbursements", response_model=ReimbursementResponse, status_code=http_status.HTTP_201_CREATED)
async def create_reimbursement(
        body: Annotated[CreateReimbursementRequest, Body(description="Reimbursement request")],
        db: Session = Depends(get_db),
):
    item: Reimbursement = Reimbursement(**body.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get("/reimbursements", response_model=list[ReimbursementResponse])
async def list_reimbursements(
        created_at_date: Annotated[date | None, Query(pattern="^\d{4}-\d{2}-\d{2}$")] = None,
        status: Annotated[ReimbursementStatus | None, Query()] = None,
        bank_id: Annotated[int | None, Query()] = None,
        db: Session = Depends(get_db),
):
    q = select(Reimbursement)

    if created_at_date:
        q = q.where(cast(Reimbursement.created_at, Date) == created_at_date)

    if status:
        q = q.where(Reimbursement.status == status.value)

    if bank_id:
        q = q.where(Reimbursement.bank_id == bank_id)

    return db.scalars(q).all()


@router.get("/reimbursements/{reimbursement_id}", response_model=ReimbursementResponse)
async def get_reimbursement(
        reimbursement_id: Annotated[int, Path()],
        db: Session = Depends(get_db),
):
    try:
        return Reimbursement.get_one(db, reimbursement_id)
    except NoResultFound:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Reimbursement not found",
        )
    except MultipleResultsFound:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Multiple reimbursements found",
        )


def mock_email(to_email: str, subject: str, body: str):
    print("Email sent")


@router.patch("/reimbursements/{reimbursement_id}")
async def update_reimbursement(
        reimbursement_id: Annotated[int, Path()],
        body: Annotated[UpdateReimbursementRequest, Body(description="Reimbursement request")],
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
):
    """
    Note: because we have no auth, we can't determine identity of the caller.
    So we do bad things by putting the decision_by_id in the request body. Normally this
    would be automagically set to the identity of the caller.

    We're treating reimbursements as immutable
    If a member wanted to make a change to their reimbursement they would have to delete and recreate.
    This means the baseline "PATCH" can just be used to update the status of the reimbursement.
    """
    try:
        reimbursement: Reimbursement = Reimbursement.get_one(db, reimbursement_id)
    except NoResultFound:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Reimbursement not found",
        )
    except MultipleResultsFound:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Multiple reimbursements found",
        )

    if reimbursement.status != ReimbursementStatus.PENDING:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Reimbursement is not pending",
        )

    reimbursement.status = body.status
    reimbursement.decision_by_id = body.decision_by_id
    reimbursement.decision_made_at = datetime.utcnow()

    db.commit()
    db.refresh(reimbursement)

    background_tasks.add_task(
        mock_email,
        reimbursement.bank_account.bank_member.email,
        "Reimbursement Status Update",
        "Your reimbursement has been " + body.status.value
    )

    return reimbursement


@router.delete("/reimbursements/{reimbursement_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_reimbursement(
        reimbursement_id: Annotated[int, Path()],
        db: Session = Depends(get_db),
):
    try:
        reimbursement: Reimbursement = Reimbursement.get_one(db, reimbursement_id)
    except NoResultFound:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Reimbursement not found",
        )
    except MultipleResultsFound:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Multiple reimbursements found",
        )
    db.delete(reimbursement)
    db.commit()
