"""update_plant_model

Revision ID: d4a7b931e2b5
Revises: c2fc9d51de02
Create Date: 2026-06-06 11:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d4a7b931e2b5"
down_revision: Union[str, None] = "c2fc9d51de02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add current_overall_quality to plants
    op.add_column(
        "plants",
        sa.Column(
            "current_overall_quality",
            sa.String(length=50),
            server_default="FAIR",
            nullable=False,
        ),
    )

    # Remove unique constraint on user_id from plants
    op.drop_constraint("plants_user_id_key", "plants", type_="unique")


def downgrade() -> None:
    # Add back unique constraint
    op.create_unique_constraint("plants_user_id_key", "plants", ["user_id"])

    # Remove current_overall_quality column
    op.drop_column("plants", "current_overall_quality")
