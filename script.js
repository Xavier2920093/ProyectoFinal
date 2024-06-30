document.getElementById("btnRegistrarRuta").addEventListener("click", function(e) {
    e.preventDefault();
    registrarRuta();
});

document.getElementById("btnObtenerRutas").addEventListener("click", function(e) {
    e.preventDefault();
    obtenerRutas();
});

function registrarRuta() {
    const ubicacion_establecimiento = JSON.parse(document.getElementById("ubicacion_establecimiento").value);
    const ubicacion_cliente = JSON.parse(document.getElementById("ubicacion_cliente").value);
    const domiciliarios = JSON.parse(document.getElementById("domiciliarios").value);

    fetch('http://127.0.0.1:8080/registrar_ruta', {
        method: "POST",
        headers: {
            "Content-Type": "application/json;charset=UTF-8"
        },
        body: JSON.stringify({
            ubicacion_establecimiento: ubicacion_establecimiento,
            ubicacion_cliente: ubicacion_cliente,
            domiciliarios: domiciliarios
        })
    })
    .then(response => response.json())
    .then((data) => {
        mostrarResultados(data);
    })
    .catch(err => console.log(err));
}

function obtenerRutas() {
    fetch('http://127.0.0.1:8080/rutas', {
        method: "GET",
        headers: {
            "Content-Type": "application/json;charset=UTF-8"
        }
    })
    .then(response => response.json())
    .then((data) => {
        mostrarResultados(data);
    })
    .catch(err => console.log(err));
}

function mostrarResultados(data) {
    const resultados = document.getElementById("resultados");
    resultados.textContent = JSON.stringify(data, null, 2);
}
