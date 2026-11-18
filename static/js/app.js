document.addEventListener("DOMContentLoaded", function () {

    const vehiculo = document.getElementById("vehiculo_id");
    const fechaInicio = document.getElementById("fecha_alquiler");
    const fechaFin = document.getElementById("fecha_devolucion");

    if (!vehiculo || !fechaInicio || !fechaFin) return;

    const diasElement = document.getElementById("dias");
    const precioElement = document.getElementById("precio");
    const totalElement = document.getElementById("total");

    function calcularTotal() {

        const inicio = fechaInicio.value;
        const fin = fechaFin.value;

        const opcion = vehiculo.options[vehiculo.selectedIndex];
        const precio = Number(opcion?.dataset.precio || 0);

        let dias = 0;

        if (inicio && fin) {
            const fecha1 = new Date(inicio + "T00:00:00");
            const fecha2 = new Date(fin + "T00:00:00");

            dias = Math.round((fecha2 - fecha1) / 86400000);

            if (dias < 0) dias = 0;
        }

        diasElement.textContent = dias;
        precioElement.textContent = "S/ " + precio.toFixed(2);
        totalElement.textContent = "S/ " + (dias * precio).toFixed(2);
    }

    vehiculo.addEventListener("change", calcularTotal);
    fechaInicio.addEventListener("change", calcularTotal);
    fechaFin.addEventListener("change", calcularTotal);

});
