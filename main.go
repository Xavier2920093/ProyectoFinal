package main

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	_ "github.com/mattn/go-sqlite3"
)

type Ruta struct {
	ID                       int            `json:"id"`
	UbicacionEstablecimiento [2]float64     `json:"ubicacion_establecimiento"`
	UbicacionCliente         [2]float64     `json:"ubicacion_cliente"`
	Domiciliarios            []Domiciliario `json:"domiciliarios"`
	Mapa                     string         `json:"mapa"`
}

type Domiciliario struct {
	ID                    int        `json:"id"`
	UbicacionDomiciliario [2]float64 `json:"ubicacion_domiciliario"`
}

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./rutas.db")
	if err != nil {
		log.Fatal(err)
	}

	createTable := `CREATE TABLE IF NOT EXISTS rutas (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		ubicacion_establecimiento TEXT,
		ubicacion_cliente TEXT,
		domiciliarios TEXT,
		mapa TEXT
	);`

	_, err = db.Exec(createTable)
	if err != nil {
		log.Fatal(err)
	}
}

func crearRuta(w http.ResponseWriter, r *http.Request) {
	var nuevaRuta Ruta
	err := json.NewDecoder(r.Body).Decode(&nuevaRuta)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	payloadBytes, _ := json.Marshal(nuevaRuta)
	resp, err := http.Post("http://localhost:5000/generar_ruta", "application/json", bytes.NewBuffer(payloadBytes))
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	var rutaConMapa Ruta
	json.Unmarshal(body, &rutaConMapa)

	rutaConMapa.UbicacionEstablecimiento = nuevaRuta.UbicacionEstablecimiento
	rutaConMapa.UbicacionCliente = nuevaRuta.UbicacionCliente
	rutaConMapa.Domiciliarios = nuevaRuta.Domiciliarios

	domiciliariosBytes, _ := json.Marshal(nuevaRuta.Domiciliarios)
	_, err = db.Exec(`INSERT INTO rutas (ubicacion_establecimiento, ubicacion_cliente, domiciliarios, mapa) VALUES (?, ?, ?, ?)`,
		fmt.Sprintf("%v", nuevaRuta.UbicacionEstablecimiento),
		fmt.Sprintf("%v", nuevaRuta.UbicacionCliente),
		string(domiciliariosBytes),
		rutaConMapa.Mapa)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(rutaConMapa)
}

func obtenerRutas(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, ubicacion_establecimiento, ubicacion_cliente, domiciliarios, mapa FROM rutas")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var rutas []Ruta
	for rows.Next() {
		var ruta Ruta
		var domiciliariosStr string
		rows.Scan(&ruta.ID, &ruta.UbicacionEstablecimiento, &ruta.UbicacionCliente, &domiciliariosStr, &ruta.Mapa)

		json.Unmarshal([]byte(domiciliariosStr), &ruta.Domiciliarios)
		rutas = append(rutas, ruta)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(rutas)
}

func main() {
	initDB()

	router := mux.NewRouter()
	router.HandleFunc("/rutas", crearRuta).Methods("POST")
	router.HandleFunc("/rutas", obtenerRutas).Methods("GET")

	log.Println("Servidor escuchando en el puerto 5001")
	http.ListenAndServe(":5001", router)
}
