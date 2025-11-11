"""add_ordenes_compra_auditoria_table

Revision ID: 95c2358b9ad6
Revises: adda8b072a38
Create Date: 2025-11-11 10:43:20.737088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95c2358b9ad6'
down_revision: Union[str, None] = 'adda8b072a38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ordenes_compra_auditoria table for order audit trail."""
    from sqlalchemy import inspect

    # Get database connection
    connection = op.get_bind()
    inspector = inspect(connection)

    # Check if table already exists
    if 'ordenes_compra_auditoria' not in inspector.get_table_names():
        op.create_table(
            'ordenes_compra_auditoria',
            sa.Column('id_auditoria', sa.BIGINT(), autoincrement=True, nullable=False),
            sa.Column('fecha_evento', sa.DateTime(), nullable=False, comment='Fecha y hora del cambio'),
            sa.Column('tipo_operacion', sa.String(length=50), nullable=False, comment='CREACION, ACTUALIZACION, ELIMINACION'),

            # Referencias de la orden de compra
            sa.Column('id_orden_compra', sa.BIGINT(), nullable=False, comment='ID de la orden de compra'),
            sa.Column('numero_oc', sa.String(length=20), nullable=False, comment='Número correlativo de la OC'),
            sa.Column('id_usuario', sa.BIGINT(), nullable=False, comment='ID del usuario que realizó el cambio'),

            # Referencias relacionadas
            sa.Column('id_cotizacion', sa.BIGINT(), nullable=True, comment='ID de la cotización relacionada'),
            sa.Column('id_cotizacion_versiones', sa.BIGINT(), nullable=True, comment='ID de la versión de cotización'),

            # Cambios de proveedor
            sa.Column('id_proveedor_anterior', sa.BIGINT(), nullable=True, comment='ID del proveedor anterior'),
            sa.Column('proveedor_anterior', sa.String(length=255), nullable=True, comment='Razón social del proveedor anterior'),
            sa.Column('id_proveedor_nuevo', sa.BIGINT(), nullable=True, comment='ID del proveedor nuevo'),
            sa.Column('proveedor_nuevo', sa.String(length=255), nullable=True, comment='Razón social del proveedor nuevo'),

            # Cambios de contacto
            sa.Column('id_contacto_anterior', sa.BIGINT(), nullable=True, comment='ID del contacto anterior'),
            sa.Column('contacto_anterior', sa.String(length=255), nullable=True, comment='Nombre del contacto anterior'),
            sa.Column('id_contacto_nuevo', sa.BIGINT(), nullable=True, comment='ID del contacto nuevo'),
            sa.Column('contacto_nuevo', sa.String(length=255), nullable=True, comment='Nombre del contacto nuevo'),

            # Cambios en productos (formato JSON)
            sa.Column('productos_agregados', sa.Text(), nullable=True, comment='Productos agregados en formato JSON'),
            sa.Column('productos_modificados', sa.Text(), nullable=True, comment='Productos modificados en formato JSON'),
            sa.Column('productos_eliminados', sa.Text(), nullable=True, comment='Productos eliminados en formato JSON'),

            # Montos
            sa.Column('monto_anterior', sa.Numeric(precision=12, scale=2), nullable=True, comment='Monto total anterior'),
            sa.Column('monto_nuevo', sa.Numeric(precision=12, scale=2), nullable=True, comment='Monto total nuevo'),

            # Otros cambios
            sa.Column('cambios_adicionales', sa.Text(), nullable=True, comment='Otros cambios (moneda, pago, entrega) en JSON'),

            # Descripción del cambio
            sa.Column('descripcion', sa.Text(), nullable=False, comment='Descripción legible del cambio'),
            sa.Column('razon', sa.Text(), nullable=True, comment='Razón del cambio (si se proporciona)'),
            sa.Column('metadata_json', sa.Text(), nullable=True, comment='Información adicional en JSON'),

            # Foreign keys
            sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], name='fk_ordenes_compra_auditoria_usuario'),
            sa.ForeignKeyConstraint(['id_cotizacion'], ['cotizacion.id_cotizacion'], name='fk_ordenes_compra_auditoria_cotizacion'),
            sa.ForeignKeyConstraint(['id_cotizacion_versiones'], ['cotizaciones_versiones.id_cotizacion_versiones'], name='fk_ordenes_compra_auditoria_version'),

            # Primary key
            sa.PrimaryKeyConstraint('id_auditoria')
        )

        # Create indexes for quick queries
        op.create_index(op.f('ix_ordenes_compra_auditoria_id_auditoria'), 'ordenes_compra_auditoria', ['id_auditoria'], unique=False)
        op.create_index(op.f('ix_ordenes_compra_auditoria_id_orden_compra'), 'ordenes_compra_auditoria', ['id_orden_compra'], unique=False)
        op.create_index(op.f('ix_ordenes_compra_auditoria_numero_oc'), 'ordenes_compra_auditoria', ['numero_oc'], unique=False)
        print("Tabla ordenes_compra_auditoria creada exitosamente")
    else:
        print("Tabla ordenes_compra_auditoria ya existe, saltando creacion")


def downgrade() -> None:
    """Remove ordenes_compra_auditoria table."""
    op.drop_index(op.f('ix_ordenes_compra_auditoria_numero_oc'), table_name='ordenes_compra_auditoria')
    op.drop_index(op.f('ix_ordenes_compra_auditoria_id_orden_compra'), table_name='ordenes_compra_auditoria')
    op.drop_index(op.f('ix_ordenes_compra_auditoria_id_auditoria'), table_name='ordenes_compra_auditoria')
    op.drop_table('ordenes_compra_auditoria')
