console.log("JS cargado");

// VARIABLES GLOBALES
let expedienteId = null;
let nombrePaciente = '';
let duiPaciente = '';
let examenesAgregados = [];

// CSRF TOKEN
const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute('content');

// FECHA ACTUAL
const hoy = new Date();
document.getElementById('fecha-hoy').value =
    hoy.toLocaleDateString('es-SV', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });

// BUSCAR CLIENTE
document.getElementById('btn-aceptar')
.addEventListener('click', function () {
    const dui = document.getElementById('dui-input').value.trim();
    if (!dui) {
        alert('Ingresá un DUI');
        return;
    }
    fetch('/examenes/buscar-cliente/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `dui=${encodeURIComponent(dui)}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.encontrado) {
            expedienteId = data.expediente_id;
            nombrePaciente = data.nombre;
            duiPaciente = dui;
            document.getElementById('nombre-paciente').value = data.nombre;
            document.getElementById('expediente-id-hidden').value = data.expediente_id;
        } else {
            alert('Cliente no encontrado');
            document.getElementById('nombre-paciente').value = '';
            expedienteId = null;
        }
    })
    .catch(error => {
        console.error(error);
        alert('Error al buscar cliente');
    });
});

// BUSCAR EXÁMENES
document.getElementById('search-examen')
.addEventListener('input', function () {
    const query = this.value.trim();
    const dropdown = document.getElementById('dropdown-examenes');
    if (!query) {
        dropdown.classList.add('hidden');
        return;
    }
    fetch('/examenes/buscar-examenes/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `q=${encodeURIComponent(query)}`
    })
    .then(res => res.json())
    .then(data => {
        dropdown.innerHTML = '';
        if (data.examenes.length === 0) {
            dropdown.classList.add('hidden');
            return;
        }
        data.examenes.forEach(examen => {
            const item = document.createElement('div');
            item.classList.add('dropdown-item');
            item.textContent = examen.nombre;
            item.addEventListener('click', function () {
                agregarExamen(examen);
                dropdown.classList.add('hidden');
                document.getElementById('search-examen').value = '';
            });
            dropdown.appendChild(item);
        });
        dropdown.classList.remove('hidden');
    })
    .catch(error => {
        console.error(error);
        alert('Error al buscar exámenes');
    });
});

// AGREGAR EXAMEN
function agregarExamen(examen) {
    if (!expedienteId) {
        alert('Primero buscá un cliente');
        return;
    }
    if (examenesAgregados.find(e => e.id === examen.id)) {
        alert('Este examen ya fue agregado');
        return;
    }
    examenesAgregados.push(examen);
    renderTabla();
}

// ELIMINAR EXAMEN
function eliminarExamen(id) {
    examenesAgregados = examenesAgregados.filter(e => e.id !== id);
    renderTabla();
}

// RENDERIZAR TABLA
function renderTabla() {
    const tbody = document.getElementById('tbody-examenes');
    const hiddenInputs = document.getElementById('inputs-examenes-hidden');
    tbody.innerHTML = '';
    hiddenInputs.innerHTML = '';
    let total = 0;
    examenesAgregados.forEach((examen, index) => {
        total += parseFloat(examen.precio);
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index === 0 ? duiPaciente : ''}</td>
            <td>${index === 0 ? nombrePaciente : ''}</td>
            <td>${examen.nombre}</td>
            <td>$${parseFloat(examen.precio).toFixed(2)}</td>
            <td><button type="button" onclick="eliminarExamen(${examen.id})">🗑</button></td>
        `;
        tbody.appendChild(tr);
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'examenes';
        input.value = examen.id;
        hiddenInputs.appendChild(input);
    });
    document.getElementById('total-precio').textContent = `$${total.toFixed(2)}`;
}

// GUARDAR ORDEN
document.getElementById('btn-guardar')
.addEventListener('click', function () {
    if (!expedienteId) {
        alert('Primero buscá un cliente');
        return;
    }
    if (examenesAgregados.length === 0) {
        alert('Agregá al menos un examen');
        return;
    }
    const nombreDoctor = document.getElementById('nombre-doctor').value.trim();
    const jvpm = document.getElementById('jvpm').value.trim();
    if (!nombreDoctor || !jvpm) {
        alert('Ingresá el nombre del doctor y el JVPM');
        return;
    }
    const total = document.getElementById('total-precio').textContent.replace('$', '');
    const inputTotal = document.createElement('input');
    inputTotal.type = 'hidden';
    inputTotal.name = 'total';
    inputTotal.value = total;
    document.getElementById('form-solicitud').appendChild(inputTotal);
    const form = document.getElementById('form-solicitud');
    form.action = '/examenes/previsualizar-pago/';
    form.method = 'POST';
    form.submit();
});

// CANCELAR
document.getElementById('btn-cancelar')
.addEventListener('click', function () {
    window.location.href = '/recepcionista/dashboard/';
});