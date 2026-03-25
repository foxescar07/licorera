// ===============================
// PRODUCTOS REGISTRADOS
let productos = JSON.parse(localStorage.getItem('productos')) || [
    "Cerveza Águila Light",
    "Coca-Cola",
    "Ron Medellín",
    "Whisky Old Parr"
];

// CARGAR PRODUCTOS EN SELECT
function cargarProductos() {
    const select = document.getElementById("filtroProducto");
    if (!select) return;

    select.innerHTML = '<option value="">Todos los productos</option>';

    productos.forEach(p => {
        select.innerHTML += `<option value="${p}">${p}</option>`;
    });
}

// ===============================
// STOCK DE PRODUCTOS
let stockProductos = [
    { producto: "Cerveza Águila Light", disponible: 50 },
    { producto: "Coca-Cola", disponible: 100 },
    { producto: "Ron Medellín", disponible: 30 },
    { producto: "Whisky Old Parr", disponible: 20 }
];

// ===============================
// VENTAS
let ventas = JSON.parse(localStorage.getItem('ventas')) || [];

// ===============================
function actualizarTabla() {
    mostrarFiltradas(ventas);
}

// ===============================
function aplicarFiltros() {
    const fecha = document.getElementById("fechaFiltro").value;
    const cliente = document.getElementById("filtroCliente").value.toLowerCase();
    const producto = document.getElementById("filtroProducto").value;

    let filtradas = ventas.filter(v => {
        let cumpleFecha = true;
        if (fecha) cumpleFecha = v.fecha === fecha;

        return cumpleFecha &&
               v.cliente.toLowerCase().includes(cliente) &&
               (producto === "" || v.producto === producto);
    });

    mostrarFiltradas(filtradas);
}

// ===============================
function mostrarFiltradas(lista) {

    const tabla = document.getElementById('tablaVentasBody');
    tabla.innerHTML = "";

    let totalVentas = 0;
    let totalCant = 0;
    let clientesSet = new Set();

    lista.forEach((v, index) => {

        let total = v.cantidad * v.precio;

        totalVentas += total;
        totalCant += v.cantidad;
        clientesSet.add(v.cliente);

        // Obtener stock disponible del producto
        let stock = stockProductos.find(s => s.producto === v.producto)?.disponible || 0;

        tabla.innerHTML += `
        <tr>
            <td>${v.id}</td>
            <td>${v.cliente}</td>
            <td>${v.producto}</td>
            <td>${stock}</td> <!-- Nueva columna de stock -->
            <td>${v.fecha}</td>
            <td>${v.cantidad}</td>
            <td>$${v.precio.toLocaleString()}</td>
            <td>$${total.toLocaleString()}</td>
            <td>
                <button class="btn btn-warning btn-sm" onclick="editarVenta(${index})">Editar</button>
                <button class="btn btn-danger btn-sm" onclick="eliminarVenta(${index})">Eliminar</button>
            </td>
        </tr>`;
    });

    document.getElementById("totalVentas").textContent = "$" + totalVentas.toLocaleString();
    document.getElementById("totalProductos").textContent = totalCant;
    document.getElementById("totalClientes").textContent = clientesSet.size;
}

// ===============================
function limpiarFiltros() {
    document.getElementById("fechaFiltro").value = "";
    document.getElementById("filtroCliente").value = "";
    document.getElementById("filtroProducto").value = "";
    actualizarTabla();
}

// ===============================
function eliminarVenta(index) {
    let v = ventas[index];

    // Devolver cantidad al stock
    let stockItem = stockProductos.find(s => s.producto === v.producto);
    if (stockItem) stockItem.disponible += v.cantidad;

    ventas.splice(index, 1);
    localStorage.setItem('ventas', JSON.stringify(ventas));
    actualizarTabla();
}

// ===============================
function editarVenta(index) {

    let v = ventas[index];

    let cliente = prompt("Cliente:", v.cliente);
    let producto = prompt("Producto:", v.producto);
    let fecha = prompt("Fecha (YYYY-MM-DD):", v.fecha);
    let cantidad = prompt("Cantidad:", v.cantidad);
    let precio = prompt("Precio:", v.precio);

    if (cliente && producto && fecha && cantidad && precio) {

        // Ajustar stock: devolver cantidad anterior
        let stockOld = stockProductos.find(s => s.producto === v.producto);
        if (stockOld) stockOld.disponible += v.cantidad;

        v.cliente = cliente;
        v.producto = producto;
        v.fecha = fecha;
        v.cantidad = parseInt(cantidad);
        v.precio = parseFloat(precio);

        // Restar cantidad nueva al stock
        let stockNew = stockProductos.find(s => s.producto === v.producto);
        if (stockNew) stockNew.disponible -= v.cantidad;

        localStorage.setItem('ventas', JSON.stringify(ventas));
        actualizarTabla();
    }
}

// ===============================
function generarReporteDiario() {
    let hoy = new Date().toISOString().split("T")[0];
    let ventasHoy = ventas.filter(v => v.fecha === hoy);

    let ingresos = 0;
    ventasHoy.forEach(v => ingresos += v.cantidad * v.precio);

    alert("📊 REPORTE DIARIO\n\nVentas: " + ventasHoy.length + "\nIngresos: $" + ingresos.toLocaleString());
}

// ===============================
// PROVEEDORES
let proveedores = [
    { id: 1, proveedor: "Distribuidora Norte", producto: "Cerveza Águila", fecha: "2026-03-20" },
    { id: 2, proveedor: "Bebidas Boyacá", producto: "Cerveza Poker", fecha: "2026-03-21" },
    { id: 3, proveedor: "Licores S.A", producto: "Club Colombia", fecha: "2026-03-22" }
];

function mostrarProveedores() {
    const tabla = document.getElementById('tablaProveedoresBody');
    if (!tabla) return;

    tabla.innerHTML = "";

    proveedores.forEach((p, index) => {
        tabla.innerHTML += `
        <tr>
            <td>${p.id}</td>
            <td>${p.proveedor}</td>
            <td>${p.producto}</td>
            <td>${p.fecha}</td>
            <td>
                <button class="btn btn-warning btn-sm" onclick="editarProveedor(${index})">Editar</button>
            </td>
        </tr>`;
    });
}


function editarProveedor(index) {

    let p = proveedores[index];

    let proveedor = prompt("Proveedor:", p.proveedor);
    let producto = prompt("Producto:", p.producto);
    let fecha = prompt("Fecha (YYYY-MM-DD):", p.fecha);

    if (proveedor && producto && fecha) {
        p.proveedor = proveedor;
        p.producto = producto;
        p.fecha = fecha;

        mostrarProveedores();
    }
}

// ===============================
// EJECUTAR
actualizarTabla();
mostrarProveedores();
document.addEventListener("DOMContentLoaded", cargarProductos);