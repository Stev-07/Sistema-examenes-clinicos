document.addEventListener("DOMContentLoaded", () => {
    // durará 5 segundos 
    const TIEMPO_VISIBLE = 5000; 

    const alertas = document.querySelectorAll('.alerta-global');

    alertas.forEach(alerta => {
        setTimeout(() => {
            alerta.style.animation = "desvanecerSalida 0.4s ease forwards";      

            alerta.addEventListener('animationend', (e) => {
                if (e.animationName === 'desvanecerSalida') {
                    alerta.remove();
                }
            });
        }, TIEMPO_VISIBLE);
    });
});