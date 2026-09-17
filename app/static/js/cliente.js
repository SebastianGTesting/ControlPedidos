// mesaActual se inyecta inline desde el template
let carrito = {};

function cambiarCantidad(id, delta) {
    const span = document.getElementById(`cant-${id}`);
    let val = parseInt(span.innerText) + delta;
    if (val < 1) val = 1;
    span.innerText = val;
}

function agregarAlCarrito(id, nombre, precio) {
    const cant = parseInt(document.getElementById(`cant-${id}`).innerText);
    if (carrito[id]) {
        carrito[id].cantidad += cant;
    } else {
        carrito[id] = { nombre, precio, cantidad: cant };
    }
    document.getElementById(`cant-${id}`).innerText = 1;
    actualizarUI();
}

function eliminarItem(id) {
    delete carrito[id];
    actualizarUI();
}

function actualizarUI() {
    const lista = document.getElementById('lista-carrito');
    lista.innerHTML = '';
    let total = 0;
    let itemsCount = 0;

    for (const [id, item] of Object.entries(carrito)) {
        const subtotal = item.precio * item.cantidad;
        total += subtotal;
        itemsCount += item.cantidad;

        lista.innerHTML += `
            <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                <div>
                    <h6 class="mb-0 fw-bold">${item.nombre}</h6>
                    <small class="text-muted">${item.cantidad} x $ ${item.precio.toLocaleString()}</small>
                </div>
                <div class="d-flex align-items-center gap-3">
                    <span class="fw-bold">$ ${subtotal.toLocaleString()}</span>
                    <button class="btn btn-sm btn-outline-danger border-0" onclick="eliminarItem(${id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </li>
        `;
    }

    if (Object.keys(carrito).length === 0) {
        lista.innerHTML = '<p class="text-center text-muted py-3">Tu carrito está vacío.</p>';
    }

    const formattedTotal = '$ ' + total.toLocaleString();
    document.getElementById('total-carrito').innerText = formattedTotal;
    document.getElementById('modal-total').innerText = formattedTotal;
    document.getElementById('cont-carrito').innerText = itemsCount;
}

function confirmarPedido() {
    if (Object.keys(carrito).length === 0) {
        alert('Agrega al menos un producto al carrito.');
        return;
    }

    fetch('/api/pedido', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mesa: mesaActual, carrito })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'ok') {
                alert(data.mensaje);
                carrito = {};
                actualizarUI();
                bootstrap.Modal.getInstance(document.getElementById('modalCarrito')).hide();
            }
        });
}
