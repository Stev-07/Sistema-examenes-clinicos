document.addEventListener("DOMContentLoaded", () => {

    // --- 1. FUNCIONES DE VALIDACIÓN DE ENTRADAS ---
    // Evitan que el usuario escriba números donde van letras o viceversa
    function soloLetras(input) {
        if (!input) return;
        input.addEventListener("input", function () {
            this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "");
        });
    }

    function soloNumeros(input, maxLength) {
        if (!input) return;
        input.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "").slice(0, maxLength);
        });
    }

    // Aplicamos las restricciones a tus campos del formulario
    soloLetras(document.getElementById("id_first_name"));
    soloLetras(document.getElementById("id_last_name"));
    soloNumeros(document.getElementById("id_n_dui"), 9);
    soloNumeros(document.getElementById("buscar-dui"), 9);


    // --- 2. LÓGICA ÚNICA DE BÚSQUEDA ---
    const btnBuscar = document.getElementById("btn-buscar-cliente");
    const inputDui = document.getElementById("buscar-dui"); // ID real de tu barra de búsqueda en el HTML

    if (btnBuscar && inputDui) {
        btnBuscar.addEventListener("click", function () {
            const dui = inputDui.value.trim();

            if (dui === "") {
                alert("Por favor, ingresá un DUI para buscar.");
                return;
            }

            // Hacemos la consulta a la URL que configuraste en tu views.py
            fetch(`/patients/buscar/?dui=${dui}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Error en la respuesta del servidor");
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.encontrado) {
                        // Guardamos el ID del cliente en el input oculto para que Django sepa que es edición
                        document.getElementById("cliente_id").value = data.cliente_id;

                        // Rellenamos los campos con la información encontrada en la base de datos
                        document.getElementById("id_first_name").value = data.first_name;
                        document.getElementById("id_last_name").value = data.last_name;
                        document.getElementById("id_n_dui").value = data.n_dui;
                        document.getElementById("id_fecha_nacimiento").value = data.fecha_nacimiento;
                        document.getElementById("id_sexo").value = data.sexo;
                        document.getElementById("id_correo_electronico").value = data.correo_electronico;

                        // IMPORTANTE: Usamos 'readOnly' en lugar de 'disabled' para los inputs de texto.
                        // Si usás 'disabled', el navegador NO envía esos campos en el POST y Django tira error de formulario inválido.
                        document.getElementById("id_first_name").readOnly = true;
                        document.getElementById("id_last_name").readOnly = true;
                        document.getElementById("id_n_dui").readOnly = true;
                        document.getElementById("id_fecha_nacimiento").readOnly = true;
                        
                        // Para el select del sexo, como no soporta readOnly, lo deshabilitamos
                        document.getElementById("id_sexo").disabled = true; 

                        // Las contraseñas dejan de ser obligatorias porque los datos ya existen
                        const pass1 = document.getElementById('id_password1');
                        const pass2 = document.getElementById('id_password2');
                        if (pass1) pass1.removeAttribute('required');
                        if (pass2) pass2.removeAttribute('required');

                        alert("Cliente encontrado. Solo podés editar el correo y la contraseña.");
                    } else {
                        alert(data.error || "No se encontró ningún cliente con ese DUI.");
                        document.getElementById("cliente_id").value = "";
                    }
                })
                .catch(error => {
                    console.error("Error en la petición fetch:", error);
                    alert("Ocurrió un error al buscar el cliente.");
                });
        });
    }
});