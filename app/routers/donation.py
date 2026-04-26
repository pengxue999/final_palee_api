from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.donation import DonationCreate, DonationUpdate, DonationResponse
from app.configs.response import success_response
from app.services import donation as svc
from app.services import receipt_pdf as receipt_pdf_svc

router = APIRouter(prefix="/donations", tags=["ການບໍລິຈາກ"])


@router.get("")
def get_donations(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [DonationResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນການບໍລິຈາກທັງໝົດສຳເລັດ"
    )


@router.get("/{donation_id}")
def get_donation(donation_id: int, db: Session = Depends(get_db)):
    return success_response(
        DonationResponse.model_validate(svc.get_by_id(db, donation_id)),
        "ດຶງຂໍ້ມູນການບໍລິຈາກສຳເລັດ"
    )


@router.get("/{donation_id}/certificate-pdf")
def get_donation_certificate_pdf(donation_id: int, db: Session = Depends(get_db)):
    donation = svc.get_by_id(db, donation_id)
    pdf_bytes = receipt_pdf_svc.build_donation_certificate_pdf(donation)
    filename = f'donation_certificate_{donation_id}.pdf'
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post("")
def create_donation(data: DonationCreate, db: Session = Depends(get_db)):
    return success_response(
        DonationResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກການບໍລິຈາກສຳເລັດ", 201
    )


@router.put("/{donation_id}")
def update_donation(donation_id: int, data: DonationUpdate, db: Session = Depends(get_db)):
    return success_response(
        DonationResponse.model_validate(svc.update(db, donation_id, data)),
        "ອັບເດດການບໍລິຈາກສຳເລັດ"
    )


@router.delete("/{donation_id}")
def delete_donation(donation_id: int, db: Session = Depends(get_db)):
    svc.delete(db, donation_id)
    return success_response(None, "ລຶບການບໍລິຈາກສຳເລັດ")
