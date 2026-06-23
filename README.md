# HIVETIRE — Backend Challenge

En este challenge buscamos evaluar tu capacidad para construir APIs sobre una base de código en Django/Python.

Debes trabajar sobre los modelos existentes en `core/models.py` y debes desarrollar los endpoints en la app `api/`.

---

## Requisitos previos

- Python **3.10** (recomendado)
- Postman

---

## Configuración inicial

```bash
# 1. Clonar el repositorio
git clone git@github.com:josemiguel-chvz/hivetire-challenge.git
cd hivetire-challenge

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Cargar datos de prueba
python manage.py loaddata initial_data

# 6. Levantar el servidor de desarrollo
python manage.py runserver
```

La API quedará disponible en `http://127.0.0.1:8000/`.

---

## Estructura del proyecto

```
hivetire-challenge/
├── conf/           # Configuración Django (settings, urls raíz)
├── core/           # Modelos de dominio (solo lectura)
│   └── models.py
├── api/            # App donde debes implementar todo
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

---

## Modelos existentes (`core/models.py`)

```python
class Vehicle(models.Model):
    active  = models.BooleanField()
    plate   = models.CharField()
    brand   = models.CharField()
    type    = models.CharField()
    fleet   = models.CharField()

class VehicleInspection(models.Model):
    vehicle  = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date     = models.DateTimeField()
    odometer = models.FloatField(default=0)
    status   = models.IntegerField(choices=[(1, "En Curso"), (2, "Finalizada")])
```

---

## Challenge

Los siguientes endpoints deben ser implementados utilizando los modelos existentes

### Fase 1 — Listados y filtros

#### `GET /api/vehicles/`

Lista paginada de vehículos.

| Parámetro   | Tipo   | Descripción                               |
|-------------|--------|-------------------------------------------|
| `status`    | string | Filtra por estado del vehículo            |
| `type`      | string | Filtra por tipo de vehículo               |
| `search`    | string | Búsqueda por placa (`plate`)              |

Cada elemento de la lista debe tener la siguiente estructura:

```json
{
  "id": 1,
  "plate": "ABC-123",
  "active": true,
  "brand": "Toyota",
  "type": "Camión",
  "fleet": "Norte"
}
```

#### `GET /api/inspections/`

Lista paginada de inspecciones.

| Parámetro    | Tipo   | Descripción                                      |
|--------------|--------|--------------------------------------------------|
| `status`     | int    | Filtra por estado (1 = En Curso, 2 = Finalizada) |
| `date_start` | date   | Filtra inspecciones desde esta fecha (`YYYY-MM-DD`) |
| `date_end`   | date   | Filtra inspecciones hasta esta fecha (`YYYY-MM-DD`) |

Cada elemento de la lista debe tener la siguiente estructura:

```json
{
  "id": 1,
  "vehicle_plate": "ABC-123",
  "status": 1,
  "date": "2024-06-01T10:30:00Z",
  "odometer": 152340.5
}
```

---

### Fase 2 — Detalle

#### `GET /api/vehicles/{id}/`

Retorna los datos del vehículo junto con la información de su **última inspección**:

```json
{
  "id": 1,
  "plate": "ABC-123",
  "brand": "Toyota",
  "type": "Camión",
  "fleet": "Norte",
  "active": true,
  "last_inspection": {
    "status": "Finalizada",
    "date": "2024-06-01",
    "odometer_km": 152340.5
  }
}
```

Si el vehículo no tiene inspecciones, `last_inspection` debe ser `null`.

---

### Fase 3 — Escritura

#### `POST /api/inspections/`

Crea una nueva inspección. El body recibe:

```json
{
  "vehicle_id": 1,
  "odometer_km": 152340.5
}
```

El servicio debe encargarse de la lógica de negocio:

1. **Validar** que el vehículo existe.
2. **Validar** que el vehículo está activo.
3. **Validar** que el vehículo no tiene una inspección con estado `En Curso`.
4. **Crear** la inspección con el `odometer_km` recibido.

En caso de error de validación, responder con el código HTTP apropiado y un mensaje descriptivo.

---

#### `PATCH /api/inspections/{id}/finalize/`

Finaliza una inspección existente. No requiere body.

El servicio debe:

1. **Validar** que la inspección existe.
2. **Validar** que la inspección está `En Curso` (status = 1).
3. **Actualizar** el status a `Finalizada` (status = 2).

En caso de error de validación, responder con el código HTTP apropiado y un mensaje descriptivo.

---

## Lo que se evalúa

- Correcta separación de responsabilidades.
- Validaciones claras y mensajes de error útiles.
- Paginación y filtros funcionando.
- Código limpio y legible.

---

## Entrega

Debes entregar tu proyecto en un repositorio git y darnos acceso para poder revisarlo.
