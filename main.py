from fastapi import FastAPI, HTTPException, Body, Query
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

class EnvioCreateWithArticulo(BaseModel):
    Cliente: str
    Estado: str
    Repuesto: RepuestoCreate
    PrecioUnitario: float
    
class TiendaCreate(BaseModel):
    Nombre: str
    Contacto: str = None
    Ubicacion: str
    
class EnvioCreate(BaseModel):
    Cliente: str
    Estado: str
    EnvioArticulosID: int
    

@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.get("/apiSucursales/obtenerSucursales")
async def obtener_sucursales():
    try:
        cursorE = conn.cursor()
        cursorE.execute("SELECT * FROM sucursales")
        sucursales = []

        for row in cursorE.fetchall():
            sucursal = {
                "SucursalID": row[0],
                "NombreSucursal": row[1],
                "Ubicacion": row[2],
                "NumeroContacto": row[3]
            }
            sucursales.append(sucursal)

        return sucursales
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()
        
@app.get("/apiClientes/obtenerClientesConAutos")
async def obtener_clientes_con_autos():
    try:
        cursorE = conn.cursor()
        # Use a JOIN to fetch information about clients and their associated cars
        cursorE.execute("""
            SELECT c.*, a.marca, a.modelo, a.anio
            FROM public.clientes c
            LEFT JOIN public.infoautomovil ia ON c.clienteid = ia.clienteid
            LEFT JOIN public.auto a ON ia.autoid = a.autoid
        """)
        clientes_con_autos = []

        # Use a dictionary to group cars by client
        cars_by_client = {}
        for row in cursorE.fetchall():
            cliente_id = row[0]
            # If the client is not in the dictionary, add them
            if cliente_id not in cars_by_client:
                cars_by_client[cliente_id] = {
                    "ClienteID": row[0],
                    "Nombre": row[1],
                    "TipoSeguro": row[2],
                    "Autos": []
                }
            # Add car information to the list of cars for the client
            cars_by_client[cliente_id]["Autos"].append({
                "Marca": row[3],
                "Modelo": row[4],
                "Anio": row[5]
            })

        # Convert the dictionary values to a list for the final result
        clientes_con_autos = list(cars_by_client.values())

        return clientes_con_autos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()

@app.get("/apiRepuestos/obtenerRepuestos")
async def obtener_repuestos():
    try:
        cursorE = conn.cursor()
        cursorE.execute("SELECT * FROM Repuestos")
        repuestos = []

        for row in cursorE.fetchall():
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

        return repuestos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()

@app.get("/apiRepuestos/obtenerTiendas")
async def obtener_tiendas():
    try:
        cursorE = conn.cursor()
        cursorE.execute("SELECT * FROM Tiendas")
        tiendas = []

        for row in cursorE.fetchall():
            tienda = {
                "TiendaID": row[0],
                "Nombre": row[1],
                "Contacto": row[2],
                "Ubicacion": row[3]
            }
            tiendas.append(tienda)

        return tiendas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()

@app.get("/apiRepuestos/obtenerEnvios")
async def obtener_envios():
    try:
        cursorE = conn.cursor()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Envios")
            envios = []

            for row in cursor.fetchall():
                envio = {
                    "EnvioID": row[0],
                    "Cliente": row[1],
                    "Estado": row[2],
                    "EnvioArticulosID": row[3]
                }
                envios.append(envio)

        return envios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()


@app.post("/apiRepuestos/agregarRepuesto")
async def agregar_repuesto(repuesto: RepuestoCreate):
    try:
        cursorE = conn.cursor()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Repuestos (Nombre, Marca, Anio, Cantidad, Precio, TiendaID) VALUES (%s, %s, %s, %s, %s, %s) RETURNING RepuestoID;",
                (repuesto.Nombre, repuesto.Marca, repuesto.Anio, repuesto.Cantidad, repuesto.Precio, repuesto.TiendaID)
            )
            repuesto_id = cursor.fetchone()[0]
        conn.commit()
        return {"RepuestoID": repuesto_id, **repuesto.dict()}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()

@app.post("/apiRepuestos/agregarTienda")
async def agregar_tienda(tienda: TiendaCreate):
    try:
        cursorE = conn.cursor()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Tiendas (Nombre, Contacto, Ubicacion) VALUES (%s, %s, %s) RETURNING TiendaID;",
                (tienda.Nombre, tienda.Contacto, tienda.Ubicacion)
            )
            tienda_id = cursor.fetchone()[0]
        conn.commit()
        return {"TiendaID": tienda_id, **tienda.dict()}
    except Exception as e:
        conn.rollback()@app.post("/apiEnvios/agregarEnvio")
    finally:
        cursorE.close()
        
@app.post("/apiRepuestos/agregarEnvio")
async def agregar_envio(envio: EnvioCreate):
    try:
        cursorE = conn.cursor()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Envios (Cliente, Estado, EnvioArticulosID) VALUES (%s, %s, %s) RETURNING EnvioID;",
                (envio.Cliente, envio.Estado, envio.EnvioArticulosID)
            )
            envio_id = cursor.fetchone()[0]
        conn.commit()
        return {"EnvioID": envio_id, **envio.dict()}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()

@app.put("/apiRepuestos/editarRepuesto/{repuesto_id}")
async def editar_repuesto(repuesto_id: int, repuesto_update: RepuestoCreate):
    try:
        cursorE = conn.cursor()
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

        # Obtener y devolver el repuesto actualizado
        return {"RepuestoID": repuesto_id, **repuesto_update.dict()}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursorE.close()
