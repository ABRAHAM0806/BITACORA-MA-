from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()

# =========================
# STATIC
# =========================
app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# TEMPLATES
# =========================
templates = Jinja2Templates(directory="templates")

# =========================
# ARCHIVO EXCEL
# =========================
ARCHIVO = "bitacora ma.xlsx"
HOJA = "pag1."

HORAS = ["4:00", "5:00", "6:00", "7:00", "8:00"]

DIAS = {
    "lunes": (4, 8),
    "martes": (9, 13),
    "miercoles": (14, 18),
    "jueves": (19, 23),
    "viernes": (24, 28),
}

# =========================
# UTILIDADES
# =========================
def normalizar(valor):

    if pd.isna(valor):
        return ""

    return str(valor).strip().upper()


def buscar_profesor(matricula, dia):

    resultados = []

    matricula = normalizar(matricula)
    dia = dia.lower()

    if dia not in DIAS:
        return resultados

    col_inicio, col_fin = DIAS[dia]

    try:

        df = pd.read_excel(
            ARCHIVO,
            sheet_name=HOJA,
            header=None
        )

    except Exception as e:

        print("ERROR LEYENDO EXCEL:", e)

        return resultados

    for fila in range(4, 68):

        aula = normalizar(df.iloc[fila, 0])
        grupo = normalizar(df.iloc[fila, 1])
        licenciatura = normalizar(df.iloc[fila, 2])

        for i, col in enumerate(range(col_inicio, col_fin + 1)):

            celda = normalizar(df.iloc[fila, col])

            if celda == matricula:

                resultados.append({
                    "hora": HORAS[i],
                    "aula": aula,
                    "grupo": grupo,
                    "licenciatura": licenciatura
                })

    return resultados

# =========================
# RUTA INICIO
# =========================
@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "resultados": None
        }
    )

# =========================
# BUSCAR
# =========================
@app.post("/buscar", response_class=HTMLResponse)
async def buscar(
    request: Request,
    matricula: str = Form(...),
    dia: str = Form(...)
):

    resultados = buscar_profesor(matricula, dia)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "resultados": resultados
        }
    )
