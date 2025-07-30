const response = {
  successs: true,
  message: "Listado de proveedores cargados correctamente",
  content: [{
    proveedorInfo: {
      idProveedor: 1,
      nombreProveedor: "Proveedor 1",
      direccionProveedor: "Calle 123",
      moneda: "DOLARES",
      entrega: "10 dias",
      pago: "EN EFECTIVO",
    },

    productos: [
      {
        id: 1,
        und: "UNIDAD",
        nombre: "Producto 1",
        marca: "MARCA 1",
        modelo: "MODELO 1",
        punitario: 100,
        ptotal: 100,
      },
      {
        id: 2,
        und: "UNIDAD",
        nombre: "Producto 2",
        marca: "MARCA 2",
        modelo: "MODELO 2",
        punitario: 100,
        ptotal: 100,
      },
    ],
  }],
};
