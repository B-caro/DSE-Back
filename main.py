from fastapi import FastAPI
import psycopg2

app=FastAPI()

conn = psycopg2.connect(
    dbname="DSE-Backedn",
    user="postgres",
    password="gamesalada",
    host="192.168.61.128",
    port="5432"  # Por defecto, el puerto es 5432
)

@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.get("/apiRepuestos/obtenerRepuestos")
async def root():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Repuestos")
    repuestos = []

    for row in cursor.fetchall():
        repuesto = {
            "RepuestoID": row[0],
            "Nombre": row[1],
            "Marca": row[2],
            "Anio": row[3],
            "Cantidad": row[4],
            "Precio": float(row[5]),  # Convierte el valor a decimal
            "TiendaID": row[6]
        }
        repuestos.append(repuesto)
    cursor.close()
    return repuestos

@app.get("/apiRepuestos/obtenerTiendas")
async def root():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tiendas")
    tiendas = []

    for row in cursor.fetchall():
        tienda = {
            "TiendaID": row[0],
            "Nombre": row[1],
            "Contacto": row[2],
            "Ubicacion": row[3]
        }
        tiendas.append(tienda)

    cursor.close()
    return tiendas