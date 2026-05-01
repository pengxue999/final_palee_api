from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.response import error_response, success_response
from app.schemas.donation_category import (
    DonationCategoryCreate,
    DonationCategoryResponse,
    DonationCategoryUpdate,
)
from app.services import donation_category as svc

router = APIRouter(prefix="/donation-categories", tags=["ປະເພດການບໍລິຈາກ"])


@router.get("")
def get_all_donation_categories(db: Session = Depends(get_db)):
    donation_categories = svc.get_all(db)
    return success_response(
        [
            DonationCategoryResponse.model_validate(donation_category)
            for donation_category in donation_categories
        ],
        "ດຶງຂໍ້ມູນປະເພດການບໍລິຈາກທັງໝົດສຳເລັດ",
    )


@router.get("/{donation_category_id}")
def get_donation_category(donation_category_id: int, db: Session = Depends(get_db)):
    try:
        donation_category = svc.get_by_id(db, donation_category_id)
        return success_response(
            DonationCategoryResponse.model_validate(donation_category),
            "ດຶງຂໍ້ມູນປະເພດການບໍລິຈາກສຳເລັດ",
        )
    except Exception:
        return error_response(
            "NOT_FOUND",
            "ບໍ່ພົບຂໍ້ມູນປະເພດການບໍລິຈາກ",
            404,
        )


@router.post("")
def create_donation_category(
    donation_category: DonationCategoryCreate,
    db: Session = Depends(get_db),
):
    created_donation_category = svc.create(db, donation_category)
    return success_response(
        DonationCategoryResponse.model_validate(created_donation_category),
        "ບັນທຶກປະເພດການບໍລິຈາກສຳເລັດ",
        201,
    )


@router.put("/{donation_category_id}")
def update_donation_category(
    donation_category_id: int,
    donation_category: DonationCategoryUpdate,
    db: Session = Depends(get_db),
):
    try:
        updated_donation_category = svc.update(
            db,
            donation_category_id,
            donation_category,
        )
        return success_response(
            DonationCategoryResponse.model_validate(updated_donation_category),
            "ອັບເດດປະເພດການບໍລິຈາກສຳເລັດ",
        )
    except Exception:
        return error_response(
            "NOT_FOUND",
            "ບໍ່ພົບຂໍ້ມູນປະເພດການບໍລິຈາກ",
            404,
        )


@router.delete("/{donation_category_id}")
def delete_donation_category(
    donation_category_id: int,
    db: Session = Depends(get_db),
):
    try:
        svc.delete(db, donation_category_id)
        return success_response(None, "ລຶບປະເພດການບໍລິຈາກສຳເລັດ")
    except Exception:
        return error_response(
            "NOT_FOUND",
            "ບໍ່ພົບຂໍ້ມູນປະເພດການບໍລິຈາກ",
            404,
        )