document.getElementById('btn-buscar-cliente').addEventListener('click', function () {

    const dui = document.getElementById('dui-busqueda').value;

    if (!dui) {
        alert('Ingresá un DUI para buscar.');
        return;
    }

    fetch(`/patients/buscar/?dui=${dui}`)
        .then(response => response.json())
        .then(data => {

            if (data.encontrado) {

                document.getElementById('cliente_id').value = data.cliente_id;

                document.getElementById('id_first_name').value = data.first_name;
                document.getElementById('id_last_name').value = data.last_name;
                document.getElementById('id_n_dui').value = data.n_dui;
                document.getElementById('id_fecha_nacimiento').value = data.fecha_nacimiento;
                document.getElementById('id_sexo').value = data.sexo;
                document.getElementById('id_correo_electronico').value = data.correo_electronico;

                // Bloquear campos
                document.getElementById('id_first_name').disabled = true;
                document.getElementById('id_last_name').disabled = true;
                document.getElementById('id_n_dui').disabled = true;
                document.getElementById('id_fecha_nacimiento').disabled = true;
                document.getElementById('id_sexo').disabled = true;

                // La contraseña deja de ser obligatoria
                document.getElementById('id_password1').removeAttribute('required');
                document.getElementById('id_password2').removeAttribute('required');

                alert('Cliente encontrado. Solo podés editar el correo y la contraseña.');

            } else {
                alert('No se encontró ningún cliente con ese DUI.');
            }

        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ocurrió un error al buscar el cliente.');
        });

});