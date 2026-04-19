from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.configs.response import success_response
from app.schemas.dashboard import DashboardStatsResponse
from app.services import dashboard as svc

router = APIRouter(prefix="/dashboard", tags=["ໜ້າຫຼັກ"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    academic_id: str = Query(None, description="ລະຫັດສົກຮຽນ (optional, ຖ້າບໍ່ລະບຸຈະໃຊ້ສົກຮຽນທີ່ກຳລັງດຳເນີນການ)"),
    db: Session = Depends(get_db)
):
    """
    ດຶງຂໍ້ມູນສະຖິຕິສຳລັບ Dashboard

    - ຖ້າລະບຸ academic_id: ສະແດງຂໍ້ມູນຕາມສົກຮຽນທີ່ເລືອກ
    - ຖ້າບໍ່ລະບຸ: ໃຊ້ສົກຮຽນທີ່ຍັງດຳເນີນການຢູ່
    """
    stats = svc.get_dashboard_stats(db, academic_id)
    return success_response(stats, "ດຶງຂໍ້ມູນສະຖິຕິ Dashboard ສຳເລັດ")
