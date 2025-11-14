"""
Servicio para uniformizar productos con y sin IGV.

Cuando una orden de compra tiene productos mezclados (algunos con IGV y otros sin IGV),
este servicio se encarga de normalizar todos los productos agregando IGV a los que vienen sin IGV.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

TASA_IGV = 0.18  # 18% de IGV en Perú


class IGVUniformizacionService:
    """
    Servicio para uniformizar productos con/sin IGV en órdenes de compra.
    """

    @staticmethod
    def productos_tienen_igv_mezclado(productos: List[Dict[str, Any]]) -> bool:
        """
        Detecta si hay productos con IGV mezclados (algunos con IGV y otros sin IGV).

        Args:
            productos: Lista de diccionarios con información de productos.
                      Cada producto debe tener una clave 'igv' con valor "CON IGV" o "SIN IGV".

        Returns:
            bool: True si hay productos mezclados, False si todos son iguales o lista vacía.
        """
        if not productos:
            return False

        # Obtener todos los tipos de IGV únicos
        tipos_igv = set()
        for producto in productos:
            igv = producto.get('igv', '').upper()
            if igv:
                tipos_igv.add(igv)

        # Si hay más de un tipo de IGV, están mezclados
        resultado = len(tipos_igv) > 1
        if resultado:
            logger.info(f"Detectados productos con IGV mezclado: {tipos_igv}")
        return resultado

    @staticmethod
    def agregar_igv_a_precio(precio: float) -> float:
        """
        Agrega IGV a un precio que viene sin IGV.

        Args:
            precio: Precio sin IGV

        Returns:
            float: Precio con IGV incluido (redondeado a 2 decimales)
        """
        return round(precio * (1 + TASA_IGV), 2)

    @staticmethod
    def uniformizar_productos_con_igv(productos: List[Any], campo_precio_unitario: str = 'pUnitario', campo_precio_total: str = 'ptotal') -> List[Any]:
        """
        Uniformiza una lista de productos agregando IGV a los que vienen SIN IGV.

        Este método crea nuevos objetos producto con precios actualizados para los productos
        que tienen igv="SIN IGV" y cambia su estado a "CON IGV".

        Args:
            productos: Lista de objetos producto (pueden ser Pydantic models o dicts)
            campo_precio_unitario: Nombre del campo de precio unitario (default: 'pUnitario')
            campo_precio_total: Nombre del campo de precio total (default: 'ptotal')

        Returns:
            List[Any]: Nueva lista con productos uniformizados
        """
        if not productos:
            return productos

        # Verificar si hay mezcla
        tipos_igv = set()
        for producto in productos:
            if hasattr(producto, 'igv'):
                igv = getattr(producto, 'igv', '').upper()
            elif isinstance(producto, dict):
                igv = producto.get('igv', '').upper()
            else:
                continue

            if igv:
                tipos_igv.add(igv)

        # Si no hay mezcla, no hacer nada
        if len(tipos_igv) <= 1:
            logger.debug("No hay productos con IGV mezclado, no se requiere uniformización")
            return productos

        logger.info(f"Uniformizando {len(productos)} productos con IGV mezclado: {tipos_igv}")

        # Uniformizar: agregar IGV a los productos SIN IGV
        productos_uniformizados = []
        productos_modificados = 0

        for producto in productos:
            # Obtener el tipo de IGV
            if hasattr(producto, 'igv'):
                igv = getattr(producto, 'igv', '').upper()
            elif isinstance(producto, dict):
                igv = producto.get('igv', '').upper()
            else:
                productos_uniformizados.append(producto)
                continue

            # Si el producto viene SIN IGV, agregarle IGV
            if igv == "SIN IGV":
                # Obtener precios actuales
                if hasattr(producto, campo_precio_unitario):
                    precio_unitario_actual = getattr(producto, campo_precio_unitario)
                    precio_total_actual = getattr(producto, campo_precio_total)

                    # Calcular nuevos precios con IGV
                    nuevo_precio_unitario = IGVUniformizacionService.agregar_igv_a_precio(precio_unitario_actual)
                    nuevo_precio_total = IGVUniformizacionService.agregar_igv_a_precio(precio_total_actual)

                    # Crear un nuevo objeto con los precios actualizados (para Pydantic models)
                    if hasattr(producto, 'copy'):  # Método copy de Pydantic
                        producto_actualizado = producto.copy(update={
                            campo_precio_unitario: nuevo_precio_unitario,
                            campo_precio_total: nuevo_precio_total,
                            'igv': 'CON IGV'
                        })
                    else:
                        # Intentar clonar el objeto manualmente
                        producto_actualizado = producto
                        setattr(producto_actualizado, campo_precio_unitario, nuevo_precio_unitario)
                        setattr(producto_actualizado, campo_precio_total, nuevo_precio_total)
                        setattr(producto_actualizado, 'igv', 'CON IGV')

                    productos_uniformizados.append(producto_actualizado)

                    productos_modificados += 1
                    id_prod = getattr(producto, 'idProducto', 'N/A')
                    logger.debug(f"Producto ID {id_prod}: "
                               f"P.Unit: {precio_unitario_actual} → {nuevo_precio_unitario}, "
                               f"P.Total: {precio_total_actual} → {nuevo_precio_total}")

                elif isinstance(producto, dict):
                    precio_unitario_actual = producto.get(campo_precio_unitario, 0)
                    precio_total_actual = producto.get(campo_precio_total, 0)

                    # Calcular nuevos precios con IGV
                    nuevo_precio_unitario = IGVUniformizacionService.agregar_igv_a_precio(precio_unitario_actual)
                    nuevo_precio_total = IGVUniformizacionService.agregar_igv_a_precio(precio_total_actual)

                    # Crear nuevo diccionario con valores actualizados
                    producto_actualizado = producto.copy()
                    producto_actualizado[campo_precio_unitario] = nuevo_precio_unitario
                    producto_actualizado[campo_precio_total] = nuevo_precio_total
                    producto_actualizado['igv'] = 'CON IGV'

                    productos_uniformizados.append(producto_actualizado)

                    productos_modificados += 1
                    logger.debug(f"Producto ID {producto.get('idProducto', 'N/A')}: "
                               f"P.Unit: {precio_unitario_actual} → {nuevo_precio_unitario}, "
                               f"P.Total: {precio_total_actual} → {nuevo_precio_total}")
                else:
                    # Si no se puede procesar, agregar sin cambios
                    productos_uniformizados.append(producto)
            else:
                # Producto ya tiene CON IGV, agregar sin cambios
                productos_uniformizados.append(producto)

        logger.info(f"✅ {productos_modificados} productos modificados de SIN IGV a CON IGV")
        return productos_uniformizados

    @staticmethod
    def uniformizar_productos_para_crear_oc(productos_info: List[Any]) -> List[Any]:
        """
        Método específico para uniformizar productos al crear OC.

        Args:
            productos_info: Lista de objetos ProductoInfo

        Returns:
            List[Any]: Lista con productos uniformizados
        """
        # Para crear OC, verificamos si tienen campo igv individual
        # Si no lo tienen, asumimos que todos son del mismo tipo según el IGV de la orden
        return IGVUniformizacionService.uniformizar_productos_con_igv(
            productos_info,
            campo_precio_unitario='pUnitario',
            campo_precio_total='ptotal'
        )

    @staticmethod
    def uniformizar_productos_para_editar_oc(productos_update: List[Any]) -> List[Any]:
        """
        Método específico para uniformizar productos al editar OC.

        Args:
            productos_update: Lista de objetos ProductoUpdateInfo

        Returns:
            List[Any]: Lista con productos uniformizados
        """
        return IGVUniformizacionService.uniformizar_productos_con_igv(
            productos_update,
            campo_precio_unitario='pUnitario',
            campo_precio_total='ptotal'
        )
