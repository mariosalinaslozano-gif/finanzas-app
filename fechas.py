from datetime import date
import calendar

def fecha_en_mes(año, mes, dia):
    ultimo_dia = calendar.monthrange(año, mes)[1]
    dia_real = min(dia, ultimo_dia)
    return date(año, mes, dia_real)

def proxima_fecha(dia, hoy=None):
    if hoy is None:
        hoy = date.today()
    año = hoy.year
    mes = hoy.month
    if dia < hoy.day:
        mes += 1
        if mes > 12:
            mes = 1
            año += 1
    return fecha_en_mes(año, mes, dia)
