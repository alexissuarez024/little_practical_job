# Ubicado dentro del ambiente creado, en la terminal instale la siguiente libreria
# pip install pytz

from datetime import timedelta, datetime
from pytz import timezone
import pytz

fecha_y_hora_actuales = datetime.now()
zona_horaria = timezone('America/Rosario')
fecha_y_hora_rosario = fecha_y_hora_actuales.astimezone(zona_horaria)
rosario_date = fecha_y_hora_rosario.strftime('%d-%m-%Y')
print(rosario_date)