let ultimoMaxId = 0;

function cargarPedidos() {
    fetch('/api/pedidos')
        .then(res => res.json())
        .then(data => {
            const pedidos = data.activos;
            const historial = data.historial;

            // ── Comandas activas ──────────────────────────────────────────
            const tbody = document.getElementById('tabla-pedidos');

            if (pedidos.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No hay comandas activas en este momento.</td></tr>';
            } else {
                if (pedidos.length > 0 && pedidos[0].id > ultimoMaxId && ultimoMaxId !== 0) {
                    document.getElementById('audioNotif').play().catch(() => {});
                }
                ultimoMaxId = pedidos[0].id;

                let html = '';
                pedidos.forEach(p => {
                    let badgeEstado = '';
                    if (p.estado === 'Pendiente de Pago')
                        badgeEstado = '<span class="badge bg-warning text-dark"><i class="fa-solid fa-clock me-1"></i>Pendiente Pago</span>';
                    else if (p.estado === 'Pasado a cocina')
                        badgeEstado = '<span class="badge bg-info text-dark"><i class="fa-solid fa-fire me-1"></i>En Cocina</span>';
                    else if (p.estado === 'Entregado')
                        badgeEstado = '<span class="badge bg-primary"><i class="fa-solid fa-check me-1"></i>Entregado</span>';
                    else
                        badgeEstado = `<span class="badge bg-secondary">${p.estado}</span>`;

                    let badgePago = '<span class="text-muted small">Sin Registrar</span>';
                    if (p.metodo_pago === 'Efectivo')
                        badgePago = '<span class="badge bg-success"><i class="fa-solid fa-money-bill me-1"></i>Efectivo</span>';
                    else if (p.metodo_pago)
                        badgePago = `<span class="badge bg-success"><i class="fa-solid fa-mobile-screen me-1"></i>${p.metodo_pago}</span>`;

                    html += `
                        <tr>
                            <td>
                                <span class="fw-bold d-block">#${p.id}</span>
                                <span class="badge bg-dark">Mesa ${p.mesa}</span>
                            </td>
                            <td><small class="text-secondary" style="white-space:pre-line">${p.detalle || ''}</small></td>
                            <td class="fw-bold text-success">$ ${(p.total || 0).toLocaleString()}</td>
                            <td>${badgeEstado}</td>
                            <td>${badgePago}</td>
                            <td>
                                <select class="form-select form-select-sm" onchange="evaluarEstado(${p.id}, ${p.mesa}, this.value)">
                                    <option value="" selected disabled>Cambiar...</option>
                                    <option value="Pasado a cocina">Pasado a cocina</option>
                                    <option value="Entregado">Entregado</option>
                                    <option value="Efectivo">Marcar Pago Efectivo</option>
                                    <option value="Transferencia">Marcar Pago Transferencia</option>
                                </select>
                            </td>
                        </tr>
                    `;
                });
                tbody.innerHTML = html;
            }

            // ── Arqueo de caja + historial ────────────────────────────────
            let totalCaja = 0, totalEfectivo = 0, totalTransf = 0;
            let htmlHistorial = '';

            historial.forEach(h => {
                if (h.metodo_pago === 'Efectivo') {
                    totalEfectivo += h.total;
                    totalCaja += h.total;
                } else if (h.metodo_pago) {
                    totalTransf += h.total;
                    totalCaja += h.total;
                }

                htmlHistorial += `
                    <tr>
                        <td><strong>#${h.id}</strong></td>
                        <td>Mesa ${h.mesa}</td>
                        <td><small class="text-muted">${h.fecha ? h.fecha.split(' ')[1] : '-'}</small></td>
                        <td class="fw-bold text-success">$ ${h.total.toLocaleString()}</td>
                        <td><span class="badge bg-light text-dark border">${h.estado}</span></td>
                        <td><span class="badge bg-success">${h.metodo_pago || 'Pendiente'}</span></td>
                    </tr>
                `;
            });

            document.getElementById('stat-total').innerText = '$ ' + totalCaja.toLocaleString();
            document.getElementById('stat-efectivo').innerText = '$ ' + totalEfectivo.toLocaleString();
            document.getElementById('stat-transferencia').innerText = '$ ' + totalTransf.toLocaleString();

            const tbodyHistorial = document.getElementById('tabla-historial');
            tbodyHistorial.innerHTML = historial.length === 0
                ? '<tr><td colspan="6" class="text-center text-muted py-3">Aún no hay registros en el historial.</td></tr>'
                : htmlHistorial;
        });
}

function evaluarEstado(pedidoId, mesaId, nuevoEstado) {
    if (nuevoEstado === 'Transferencia') {
        document.getElementById('pedido_id_transf').value = pedidoId;
        new bootstrap.Modal(document.getElementById('modalTransferencia')).show();
    } else if (nuevoEstado === 'Efectivo') {
        enviarEstado(pedidoId, null, 'Efectivo');
    } else if (nuevoEstado === 'Entregado') {
        document.getElementById('pedido_id_entregado').value = pedidoId;
        document.getElementById('lbl_pedido_id').innerText = '#' + pedidoId;
        document.getElementById('lbl_mesa_id').innerText = 'Mesa ' + mesaId;
        new bootstrap.Modal(document.getElementById('modalConfirmarEntregado')).show();
    } else {
        enviarEstado(pedidoId, nuevoEstado, null);
    }
}

function ejecutarEntrega() {
    const pedidoId = document.getElementById('pedido_id_entregado').value;
    enviarEstado(pedidoId, 'Entregado', null);
    bootstrap.Modal.getInstance(document.getElementById('modalConfirmarEntregado')).hide();
}

function confirmarTransferencia(metodo) {
    const pedidoId = document.getElementById('pedido_id_transf').value;
    enviarEstado(pedidoId, null, metodo);
    bootstrap.Modal.getInstance(document.getElementById('modalTransferencia')).hide();
}

function enviarEstado(pedidoId, nuevoEstado, metodoPago) {
    const formData = new FormData();
    formData.append('pedido_id', pedidoId);
    if (nuevoEstado) formData.append('nuevo_estado', nuevoEstado);
    if (metodoPago) formData.append('metodo_pago', metodoPago);

    fetch('/admin/cambiar_estado', { method: 'POST', body: formData })
        .then(() => cargarPedidos());
}

function cambiarModoPago(checked) {
    const modo = checked ? 'pagar_primero' : 'pagar_despues';
    const formData = new FormData();
    formData.append('modo', modo);
    fetch('/admin/configurar_modo', { method: 'POST', body: formData });
}

// Carga inicial y polling cada 4 segundos
cargarPedidos();
setInterval(cargarPedidos, 4000);
