# Solucion del Backend Challenge

Este documento explica la solucion implementada para el challenge 
La implementacion se concentra en la app `api/` y usa los modelos existentes de
`core/models.py` como codigo de solo lectura.

## Objetivo

El challenge pidio construir una API REST para consultar vehiculos, consultar
inspecciones, crear inspecciones y finalizar inspecciones existentes.

Los modelos disponibles son:

- `Vehicle`: representa un vehiculo de la flota.
- `VehicleInspection`: representa una inspeccion asociada a un vehiculo.

La solucion no modifica los modelos. La API adapta esos modelos al contrato HTTP
pedido por el README.

## Arquitectura

La solucion separa responsabilidades en cuatro archivos principales:

- `api/serializers.py`: define como se transforman los modelos a JSON y como se
  validan los datos de entrada.
- `api/services.py`: contiene la logica de negocio para crear y finalizar
  inspecciones.
- `api/views.py`: recibe requests HTTP, aplica filtros, pagina resultados y
  llama a serializers o services.
- `api/urls.py`: declara las rutas publicas de la API.

Esta separacion permite que la logica de negocio no quede mezclada con la capa
HTTP.

## Endpoints Implementados

### Listar vehiculos

```http
GET /api/vehicles/
```

Devuelve una lista paginada de vehiculos.

Ejemplo de respuesta:

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "plate": "BCDF-12",
      "active": true,
      "brand": "Toyota",
      "type": "Camion",
      "fleet": "Norte"
    }
  ]
}
```

Filtros soportados:

- `active`: filtra por vehiculos activos o inactivos.
- `brand`: filtra por marca.
- `type`: filtra por tipo de vehiculo.
- `fleet`: filtra por flota.
- `search`: busca por patente.
- `ordering`: ordena por campos permitidos.

Ejemplos:

```http
GET /api/vehicles/?active=true
GET /api/vehicles/?fleet=Norte
GET /api/vehicles/?search=BCD
GET /api/vehicles/?ordering=plate
GET /api/vehicles/?page=1&page_size=5
```

## Detalle de vehiculo

```http
GET /api/vehicles/{id}/
```

Devuelve los datos de un vehiculo junto con su ultima inspeccion.

Ejemplo:

```json
{
  "id": 1,
  "plate": "BCDF-12",
  "active": true,
  "brand": "Toyota",
  "type": "Camion",
  "fleet": "Norte",
  "last_inspection": {
    "status": "Finalizada",
    "date": "2025-10-15",
    "odometer_km": 77359.0
  }
}
```

Si el vehiculo no tiene inspecciones, `last_inspection` devuelve `null`.

La ultima inspeccion se obtiene ordenando por `date` descendente y luego por
`id` descendente. Esto resuelve casos donde dos inspecciones tengan la misma
fecha.

## Listar inspecciones

```http
GET /api/inspections/
```

Devuelve una lista paginada de inspecciones.

Ejemplo:

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "status": 1,
      "date": "2026-06-24T17:30:00Z",
      "odometer": 80000.0,
      "vehicle_id": 1,
      "vehicle_plate": "BCDF-12"
    }
  ]
}
```

Filtros soportados:

- `status`: filtra por estado de inspeccion.
- `vehicle_id`: filtra por vehiculo.
- `vehicle_plate`: busca por patente del vehiculo.
- `date_from`: filtra desde una fecha.
- `date_to`: filtra hasta una fecha.
- `ordering`: ordena por campos permitidos.

Ejemplos:

```http
GET /api/inspections/?status=1
GET /api/inspections/?status=2
GET /api/inspections/?vehicle_id=1
GET /api/inspections/?vehicle_plate=BCD
GET /api/inspections/?ordering=-date
GET /api/inspections/?page=1&page_size=5
```

Para evitar consultas N+1, el listado de inspecciones usa
`select_related("vehicle")`. Como `VehicleInspection.vehicle` es una
`ForeignKey`, Django resuelve la relacion con un JOIN y evita una consulta extra
por cada inspeccion al serializar `vehicle_plate`.

## Crear inspeccion

```http
POST /api/inspections/
```

Body:

```json
{
  "vehicle_id": 1,
  "odometer_km": 80000
}
```

Respuesta exitosa:

```http
201 Created
```

```json
{
  "id": 10,
  "status": 1,
  "date": "2026-06-24T17:40:00Z",
  "odometer": 80000.0,
  "vehicle_id": 1,
  "vehicle_plate": "BCDF-12"
}
```

Reglas de negocio:

- El vehiculo debe existir.
- El vehiculo debe estar activo.
- El vehiculo no debe tener otra inspeccion con `status = 1`.
- La inspeccion se crea con `status = 1`, que representa `En Curso`.

Errores esperados:

```http
404 Not Found
```

```json
{
  "detail": "Vehiculo no encontrado"
}
```

```http
400 Bad Request
```

```json
{
  "detail": "Vehiculo inactivo"
}
```

```http
409 Conflict
```

```json
{
  "detail": "El vehiculo ya tiene una inspeccion en curso"
}
```

## Finalizar inspeccion

```http
PATCH /api/inspections/{id}/finalize/
```

Este endpoint no requiere body.

Respuesta exitosa:

```http
200 OK
```

```json
{
  "id": 10,
  "status": 2,
  "date": "2026-06-24T17:40:00Z",
  "odometer": 80000.0,
  "vehicle_id": 1,
  "vehicle_plate": "BCDF-12"
}
```

Reglas de negocio:

- La inspeccion debe existir.
- La inspeccion debe estar en curso (`status = 1`).
- Al finalizar, el estado pasa a `status = 2`, que representa `Finalizada`.

Errores esperados:

```http
404 Not Found
```

```json
{
  "detail": "Inspeccion no encontrada"
}
```

```http
400 Bad Request
```

```json
{
  "detail": "La inspeccion ya fue finalizada"
}
```

## Pruebas Manuales con Postman

### 1. Buscar un vehiculo activo

```http
GET http://127.0.0.1:8000/api/vehicles/?active=true
```

Tomar un `id` de la respuesta.

### 2. Crear una inspeccion

```http
POST http://127.0.0.1:8000/api/inspections/
```

Body:

```json
{
  "vehicle_id": 1,
  "odometer_km": 80000
}
```

La respuesta debe ser `201 Created` y debe devolver una inspeccion con
`status = 1`.

### 3. Ver inspecciones en curso

```http
GET http://127.0.0.1:8000/api/inspections/?status=1
```

Tomar el `id` de una inspeccion en curso.

### 4. Finalizar la inspeccion

```http
PATCH http://127.0.0.1:8000/api/inspections/{id}/finalize/
```

No enviar body.

La respuesta debe ser `200 OK` y debe devolver la inspeccion con `status = 2`.

### 5. Verificar el detalle del vehiculo

```http
GET http://127.0.0.1:8000/api/vehicles/{vehicle_id}/
```

El campo `last_inspection` debe mostrar la ultima inspeccion del vehiculo.

## Tests Automatizados

El proyecto incluye  un test en `api/tests.py`.

El test valida que no se pueda crear una nueva inspeccion para un vehiculo que
ya tiene una inspeccion en curso.

Comando:

```bash
python manage.py test api
```

Resultado esperado:

```text
OK
```

## Decisiones Tecnicas

- Se usaron serializers para adaptar los nombres del modelo al contrato de la
  API, por ejemplo `odometer` como `odometer_km` en la creacion y detalle.
- La logica de negocio se ubico en services para evitar views con demasiada
  responsabilidad.
- Se uso paginacion para que los listados escalen mejor.
- Se restringio el ordenamiento a campos permitidos para evitar parametros
  arbitrarios.
- Se uso `select_related("vehicle")` en inspecciones para evitar el problema
  N+1.
- Se usaron status codes HTTP distintos para representar errores de existencia,
  validacion y conflicto de estado.

