"""add_registro_compra_auditoria_table

Revision ID: adda8b072a38
Revises: d333fc65430f
Create Date: 2025-10-17 16:53:29.394169

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'adda8b072a38'
down_revision: Union[str, None] = 'd333fc65430f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add registro_compra_auditoria table for audit trail."""
    from sqlalchemy import inspect

    # Get database connection
    connection = op.get_bind()
    inspector = inspect(connection)

    # Check if table already exists
    if 'registro_compra_auditoria' not in inspector.get_table_names():
        op.create_table(
            'registro_compra_auditoria',
            sa.Column('id_auditoria', sa.BIGINT(), autoincrement=True, nullable=False),
            sa.Column('fecha_evento', sa.DateTime(), nullable=False, comment='Fecha y hora del cambio'),
            sa.Column('tipo_operacion', sa.String(length=50), nullable=False, comment='CREACION, ACTUALIZACION, ELIMINACION'),
            sa.Column('tipo_entidad', sa.String(length=50), nullable=False, comment='REGISTRO_COMPRA, ORDEN_COMPRA, REGISTRO_COMPRA_ORDEN'),
            sa.Column('compra_id', sa.BIGINT(), nullable=True, comment='ID del registro de compra (null si se eliminó)'),
            sa.Column('id_orden', sa.Integer(), nullable=True, comment='ID de la orden de compra'),
            sa.Column('id_cotizacion', sa.Integer(), nullable=True, comment='ID de la cotización'),
            sa.Column('id_cotizacion_versiones', sa.Integer(), nullable=True, comment='ID de la versión de cotización'),
            sa.Column('id_usuario', sa.Integer(), nullable=True, comment='ID del usuario que realizó el cambio'),
            sa.Column('datos_anteriores', sa.Text(), nullable=True, comment='Estado anterior en formato JSON'),
            sa.Column('datos_nuevos', sa.Text(), nullable=True, comment='Estado nuevo en formato JSON'),
            sa.Column('monto_anterior', sa.Numeric(precision=12, scale=2), nullable=True, comment='Monto total anterior'),
            sa.Column('monto_nuevo', sa.Numeric(precision=12, scale=2), nullable=True, comment='Monto total nuevo'),
            sa.Column('descripcion', sa.Text(), nullable=False, comment='Descripción legible del cambio'),
            sa.Column('razon', sa.Text(), nullable=True, comment='Razón del cambio (si se proporciona)'),
            sa.Column('metadata_json', sa.Text(), nullable=True, comment='Información adicional en JSON'),
            sa.PrimaryKeyConstraint('id_auditoria')
        )

        # Create indexes for quick queries
        op.create_index(op.f('ix_registro_compra_auditoria_id_auditoria'), 'registro_compra_auditoria', ['id_auditoria'], unique=False)
        op.create_index(op.f('ix_registro_compra_auditoria_compra_id'), 'registro_compra_auditoria', ['compra_id'], unique=False)
        op.create_index(op.f('ix_registro_compra_auditoria_id_cotizacion'), 'registro_compra_auditoria', ['id_cotizacion'], unique=False)
        op.create_index(op.f('ix_registro_compra_auditoria_id_orden'), 'registro_compra_auditoria', ['id_orden'], unique=False)
        print("Tabla registro_compra_auditoria creada exitosamente")
    else:
        print("Tabla registro_compra_auditoria ya existe, saltando creacion")


def downgrade() -> None:
    """Remove registro_compra_auditoria table."""
    op.drop_index(op.f('ix_registro_compra_auditoria_id_orden'), table_name='registro_compra_auditoria')
    op.drop_index(op.f('ix_registro_compra_auditoria_id_cotizacion'), table_name='registro_compra_auditoria')
    op.drop_index(op.f('ix_registro_compra_auditoria_compra_id'), table_name='registro_compra_auditoria')
    op.drop_index(op.f('ix_registro_compra_auditoria_id_auditoria'), table_name='registro_compra_auditoria')
    op.drop_table('registro_compra_auditoria')
