document.addEventListener("DOMContentLoaded", () => {

    const buscarDui = document.getElementById("buscar-dui");

    if (buscarDui) {

        buscarDui.addEventListener("input", function () {

            this.value = this.value
                .replace(/\D/g, "")
                .slice(0, 9);

        });

    }

});

console.log("JS cargado correctamente");