from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import psycopg2

app=FastAPI()

conn = psycopg2.connect(
    user="fl0user",
    password="Mfmn8w1pRjlq",
    dbname="DSE-Backend",
    host="ep-broad-resonance-93484468.us-east-2.aws.neon.fl0.io",    
    port="5432",
    sslmode="require"
)

class RepuestoCreate(BaseModel):
    Nombre: str
    Marca: str = None
    Anio: int = None
    Cantidad: int
    Precio: float
    TiendaID: int

class TiendaCreate(BaseModel):
    Nombre: str
    Contacto: str = None
    Ubicacion: str

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

@app.post("/apiRepuestos/agregarRepuesto")
async def agregar_repuesto(repuesto: RepuestoCreate):
    cursorE = conn.cursor()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Repuestos (Nombre, Marca, Anio, Cantidad, Precio, TiendaID) VALUES (%s, %s, %s, %s, %s, %s) RETURNING RepuestoID;",
                (repuesto.Nombre, repuesto.Marca, repuesto.Anio, repuesto.Cantidad, repuesto.Precio, repuesto.TiendaID)
            )
            repuesto_id = cursor.fetchone()[0]
        conn.commit()
        cursorE.close()
        return {"RepuestoID": repuesto_id, **repuesto.dict()}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()

@app.post("/apiRepuestos/agregarTienda")
async def agregar_tienda(tienda: TiendaCreate):
    cursorE = conn.cursor()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Tiendas (Nombre, Contacto, Ubicacion) VALUES (%s, %s, %s) RETURNING TiendaID;",
                (tienda.Nombre, tienda.Contacto, tienda.Ubicacion)
            )
            tienda_id = cursor.fetchone()[0]
        conn.commit()
        cursorE.close()
        return {"TiendaID": tienda_id, **tienda.dict()}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()

@app.put("/apiRepuestos/editarRepuesto/{repuesto_id}")
async def editar_repuesto(repuesto_id: int, repuesto_update: RepuestoCreate):
    cursorE = conn.cursor()
    try:
        with conn.cursor() as cursor:
            # Verificar si el repuesto existe
            cursor.execute("SELECT * FROM Repuestos WHERE RepuestoID = %s;", (repuesto_id,))
            existing_repuesto = cursor.fetchone()

            if not existing_repuesto:
                raise HTTPException(status_code=404, detail="Repuesto no encontrado")

            # Construir la actualización del repuesto
            update_query = "UPDATE Repuestos SET "
            update_values = []

            for field, value in repuesto_update.dict(exclude_unset=True).items():
                update_query += f"{field} = %s, "
                update_values.append(value)

            update_query = update_query.rstrip(", ")  # Eliminar la coma final
            update_query += f" WHERE RepuestoID = {repuesto_id};"

            # Ejecutar la actualización
            cursor.execute(update_query, update_values)
            conn.commit()
            cursorE.close()

        # Obtener y devolver el repuesto actualizado
        return {"RepuestoID": repuesto_id, **repuesto_update.dict()}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()