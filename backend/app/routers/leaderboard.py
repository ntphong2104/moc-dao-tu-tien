"""Router Leaderboard — Bảng xếp hạng Tu Vi."""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.plant import Plant
from app.schemas.leaderboard import LeaderboardResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(20, ge=1, le=100, description="Số lượng kết quả (1-100)"),
    db: AsyncSession = Depends(get_db),
) -> LeaderboardResponse:
    """Lấy bảng xếp hạng cây có Tu Vi cao nhất.

    Sắp xếp giảm dần theo total_exp.
    """
    stmt = (
        select(Plant)
        .options(
            selectinload(Plant.user),
            selectinload(Plant.current_rank),
        )
        .order_by(Plant.total_exp.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    plants = result.scalars().all()

    # Tổng số cây
    from sqlalchemy import func

    count_result = await db.execute(select(func.count(Plant.id)))
    total_count = count_result.scalar() or 0

    entries = []
    for i, plant in enumerate(plants, 1):
        entries.append(
            {
                "rank": i,
                "plant_name": plant.name,
                "owner_display_name": plant.user.display_name
                if plant.user
                else "Unknown",
                "total_exp": plant.total_exp,
                "rank_name": plant.current_rank.name
                if plant.current_rank
                else "Phàm Mộc",
                "plant_id": str(plant.id),
            }
        )

    return LeaderboardResponse(
        entries=entries,
        total_count=total_count,
    )
