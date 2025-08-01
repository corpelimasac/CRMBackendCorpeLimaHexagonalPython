from app.core.ports.repositories.ordenes_compra_repository import OrdenesCompraRepositoryPort
from app.core.domain.entities.ordenes_compra import OrdenesCompra
from sqlalchemy.orm import Session
from app.adapters.outbound.database.models.ordenes_compra_model import OrdenesCompraModel
from app.adapters.outbound.database.models.ordenes_compra_detalles_model import OrdenesCompraDetallesModel
from datetime import datetime

class OrdenesCompraRepository(OrdenesCompraRepositoryPort):

    def __init__(self, db: Session):
        self.db = db

    def save(self, order: OrdenesCompra) -> OrdenesCompra:
        try:
            # --- 1. Mapeo: Entidad de Dominio -> Modelo de la Orden Principal ---
            # Nota: Faltan campos en tu entidad que sí están en el modelo de DB (ej. correlative, id_usuario).
            # Deberás añadirlos a la entidad o gestionarlos aquí.
            
            # 1. Obtener el último correlativo
            last_correlative = self.db.query(OrdenesCompraModel).order_by(OrdenesCompraModel.id_orden.desc()).first()
            if last_correlative:
                last_number = int(last_correlative.correlative.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            # 2. Generar el correlativo
            new_correlative = f"OC-{new_number:03d}"

            db_order = OrdenesCompraModel(
                id_cotizacion=order.id_cotizacion,
                id_proveedor=order.id_proveedor,
                moneda=order.moneda,
                pago=order.pago,
                entrega=order.entrega,
                version=order.id_version,
                fecha_creacion=datetime.now(),
                correlative=new_correlative, 
                id_usuario=order.id_usuario
            )

            # --- 2. Insertar la Orden Principal ---
            self.db.add(db_order)
            # Hacemos un "flush" para que la base de datos asigne el ID autoincremental
            # sin hacer un commit completo de la transacción.
            self.db.flush() 

            # --- 3. Mapeo e Inserción de los Detalles ---
            for item in order.items:
                db_detail = OrdenesCompraDetallesModel(
                    id_orden=db_order.id_orden, # <-- Usamos el ID recién generado
                    id_producto=item.id_producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.p_unitario,
                    total=item.p_total
                )
                self.db.add(db_detail)

            # --- 4. Confirmar la Transacción ---
            self.db.commit()
            
            # (Opcional) Refrescar el objeto para tener todos los datos de la DB
            #self.db.refresh(db_order) 
            
            # Devuelves la entidad original o una actualizada con el nuevo ID
            return order

        except Exception as e:
            # Si algo falla, revertimos todos los cambios de esta transacción
            self.db.rollback()
            print(f"Error al guardar la orden de compra: {e}")
            raise e # Vuelve a lanzar la excepción para que el caso de uso la maneje