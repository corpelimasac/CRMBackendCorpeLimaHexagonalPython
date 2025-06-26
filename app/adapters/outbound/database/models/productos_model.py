from sqlalchemy import Column, Integer, VARCHAR, Date, Boolean, ForeignKey
from datetime import datetime
from .base import Base

class ProductosModel(Base):
  __tablename__ = "productos"
  id_producto= Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
  nombre = Column(VARCHAR(255), nullable=True)
  codigo_empresa = Column(VARCHAR(255), nullable=True)
  modelo_marca = Column(VARCHAR(255), nullable=True)
  descripcion_corta = Column(VARCHAR(255), nullable=True)
  descripcion_larga = Column(VARCHAR(255), nullable=True)
  fecha_creacion = Column(Date, default=datetime.now, nullable=False)
  estado = Column(Boolean, default=True, nullable=True)
  fecha_modificacion = Column(Date, default=datetime.now, onupdate=datetime.now, nullable=True) 
  fecha_modificacion_precio = Column(Date, default=datetime.now, onupdate=datetime.now, nullable=True)
  id_producto_documento = Column(Integer, nullable=True)
  descontinuado = Column(Boolean, default=True, nullable=True)

  # Relación con la tabla de marcas
  id_marca = Column(Integer, ForeignKey("marcas.id_marca"), nullable=True)

  # Relación con la tabla de categorias
  id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=True)

  # Relación con la tabla de subcategorias
  id_subcat = Column(Integer, ForeignKey("subcategoria.id_subcat"), nullable=True)

  # Relación con la tabla de elementos especificos
  id_elemespec = Column(Integer, ForeignKey("elemento_especifico.id_elemespec"), nullable=True)

  # Relación con la tabla de proveedores
  id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)

  # Relación con la tabla de unidades de medida
  id_unidad_medida = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=True)
