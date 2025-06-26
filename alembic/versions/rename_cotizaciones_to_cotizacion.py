"""rename cotizaciones to cotizacion

Revision ID: rename_cotizaciones_to_cotizacion
Revises: 78a26b97bf1e
Create Date: 2025-06-26 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'rename_cotizaciones_to_cotizacion'
down_revision: Union[str, None] = '78a26b97bf1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renombrar la tabla de cotizaciones a cotizacion
    op.rename_table('cotizaciones', 'cotizacion')


def downgrade() -> None:
    # Revertir el cambio: renombrar de cotizacion a cotizaciones
    op.rename_table('cotizacion', 'cotizaciones') 