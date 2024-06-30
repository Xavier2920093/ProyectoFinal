import json
import sqlite3
import math
from http.server import BaseHTTPRequestHandler, HTTPServer

# Conectar a la base de datos SQLite
conn = sqlite3.connect('rutas.db')
c = conn.cursor()

# Crear tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS rutas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ubicacion_establecimiento TEXT,
    ubicacion_cliente TEXT,
    domiciliarios TEXT,
    ruta TEXT
)''')
conn.commit()

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        if self.path == '/registrar_ruta':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            ubicacion_establecimiento = data.get('ubicacion_establecimiento')
            ubicacion_cliente = data.get('ubicacion_cliente')
            domiciliarios = data.get('domiciliarios')

            if ubicacion_establecimiento and ubicacion_cliente and len(domiciliarios) == 3:
                ruta = self.generar_ruta(ubicacion_establecimiento, ubicacion_cliente, domiciliarios)
                self.registrar_ruta(ubicacion_establecimiento, ubicacion_cliente, domiciliarios, ruta)
                self._set_headers(200)
                self.wfile.write(json.dumps({'ruta': ruta}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Datos incompletos o incorrectos'}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Recurso no encontrado'}).encode())

    def do_GET(self):
        if self.path == '/rutas':
            self.obtener_rutas()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Recurso no encontrado'}).encode())

    def distancia(self, a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def generar_ruta(self, ubicacion_establecimiento, ubicacion_cliente, domiciliarios):
        min_dist = float('inf')
        domiciliario_cercano = None

        for domiciliario in domiciliarios:
            dist = self.distancia(ubicacion_establecimiento, domiciliario['ubicacion'])
            if dist < min_dist:
                min_dist = dist
                domiciliario_cercano = domiciliario

        return {
            'domiciliario_cercano_id': domiciliario_cercano['id'],
            'distancia': min_dist,
            'ruta': f"El domiciliario más cercano es el ID {domiciliario_cercano['id']} con una distancia de {min_dist:.2f} unidades."
        }

    def registrar_ruta(self, ubicacion_establecimiento, ubicacion_cliente, domiciliarios, ruta):
        c.execute("INSERT INTO rutas (ubicacion_establecimiento, ubicacion_cliente, domiciliarios, ruta) VALUES (?, ?, ?, ?)",
                  (json.dumps(ubicacion_establecimiento), json.dumps(ubicacion_cliente), json.dumps(domiciliarios), json.dumps(ruta)))
        conn.commit()

    def obtener_rutas(self):
        c.execute("SELECT * FROM rutas")
        rutas = c.fetchall()
        rutas_formateadas = []
        for ruta in rutas:
            try:
                rutas_formateadas.append({
                    'id': ruta[0],
                    'ubicacion_establecimiento': json.loads(ruta[1]),
                    'ubicacion_cliente': json.loads(ruta[2]),
                    'domiciliarios': json.loads(ruta[3]),
                    'ruta': json.loads(ruta[4])
                })
            except json.JSONDecodeError:
                print(f"Error decodificando JSON para la ruta con ID {ruta[0]}")
                continue
        self._set_headers(200)
        self.wfile.write(json.dumps(rutas_formateadas).encode())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Servidor corriendo en el puerto {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
