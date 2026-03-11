function actualizarReloj() {
    const ahora = new Date();
    let horas = ahora.getHours();
    let minutos = ahora.getMinutes();
    let ampm = horas >= 12 ? "p. m." : "a. m.";

    horas = horas % 12;
    horas = horas ? horas : 12;
    minutos = minutos < 10 ? "0" + minutos : minutos;

    const relojElement = document.getElementById("reloj");
    const fechaElement = document.getElementById("fecha");

    if (relojElement) {
        relojElement.innerHTML = horas + ":" + minutos + " " + ampm;
    }

    if (fechaElement) {
        const dias = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
        const meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
        fechaElement.innerHTML = dias[ahora.getDay()] + ", " + ahora.getDate() + " de " + meses[ahora.getMonth()];
    }
}

setInterval(actualizarReloj, 1000);
actualizarReloj();