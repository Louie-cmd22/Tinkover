"""blogs: add cascade deletion to user_id foreignkey and set nullable to false

Revision ID: 6fd7af26aac0
Revises: 8b4cadc874fc
Create Date: 2026-08-18 18:50:14.950537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fd7af26aac0'
down_revision: Union[str, Sequence[str], None] = '8b4cadc874fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("blogs") as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=False
        )

        batch_op.drop_constraint(
            "fk_blogs_user_id_users",
            type_="foreignkey"
        )

        batch_op.create_foreign_key(
            "fk_blogs_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE"
        )

def downgrade() -> None:
    with op.batch_alter_table("blogs") as batch_op:
        batch_op.drop_constraint(
            "fk_blogs_user_id_users",
            type_="foreignkey"
        )

        batch_op.create_foreign_key(
            "fk_blogs_user_id_users",
            "users",
            ["user_id"],
            ["id"]
        )

        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=True
        )