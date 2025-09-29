# HubSpot Data Processing Script

Este script permite extraer y procesar datos de HubSpot (leads y deals) y almacenarlos en MongoDB con transformaciones específicas.

## Decisiones Técnicas

Se seleccionó **Python** como lenguaje para extracción y conversión (ETL) ya que es ampliamente utilizado para este propósito, además posee herramientas como Pandas, Polars y otras que facilitan enormemente la manipulación de datos.

Se eligió **MongoDB** por su potencia en agregaciones y facilidad en bulk upserts, aunque esto es un tema de gustos personales. Usar BigQuery, RedShift u otras bases de datos para analítica es igualmente válido, pero por comodidad, facilidad de configuración y levantamiento de la base de datos se opte por MongoDB.

El script obtiene los datos desde HubSpot y los procesa utilizando la librería oficial de Python, guarda los datos en la base de datos cambiando el nombre de los campos (necesario cuando se debe homologar con otras fuentes de datos), además hace agrupaciones para crear tablas resumen, todo esto usando upserts para actualizaciones o inserciones. Incluye conversión de campos fecha y montos a tipo decimal para garantizar la integridad y consistencia de los datos.

## Herramientas Utilizadas

- **Python**

  - Pandas
  - PyMongo
  - hubspot
- **MongoDB**
- **NestJS (API) VER AL FINAL LOS ENDPOINTS**

## Arquitectura del proyecto y Ejecución

El proyecto utiliza la **librería oficial de HubSpot para Python** (`hubspot`) para conectarse a la API de HubSpot. El archivo `hubspot_client.py` contiene una clase personalizada que encapsula los métodos necesarios para:

- Obtener datos de leads y deals desde HubSpot
- Manejar la autenticación con la API
- Cargar archivos JSON para pruebas
- Proporcionar una interfaz simplificada para las operaciones requeridas

## Cómo ejecutar el script

### Requisitos previos

- Python 3.8+
- Dependencias instaladas (ver `pyproject.toml`)
- Archivo `.env.develop` configurado con las llaves de HubSpot y MongoDB
- Conexión a MongoDB configurada

### Comandos básicos

```bash
# Procesar leads
uv run python mainProcess.py --type leads

# Procesar deals
uv run python mainProcess.py --type deals
```

## Configuración

El archivo `.env.develop` contiene las llaves necesarias para el funcionamiento del script:

### Variables de entorno requeridas:

```
HUBSPOT_API_KEY=tu_api_key_de_hubspot_aqui
MONGODB_URI=tu_conexion_mongodb_aqui

```

**Importante**: El archivo `.env.develop` debe contener tanto la llave de HubSpot como las credenciales de MongoDB para que el script funcione correctamente.

## Procesamiento de Leads

### Transformaciones de campos

El script realiza las siguientes transformaciones en los datos de leads:

| Campo original               | Campo transformado | Descripción                                                  |
| ---------------------------- | ------------------ | ------------------------------------------------------------- |
| `firstname`                | `first_name`     | Nombre del lead                                               |
| `lastname`                 | `last_name`      | Apellido del lead                                             |
| `hs_lead_status`           | `lead_status`    | Estado del lead                                               |
| `firstname` + `lastname` | `full_name`      | **Campo agregado**: Concatenación de nombre y apellido |

### Proceso de datos

1. **Extracción**: Se obtienen los leads desde HubSpot
2. **Transformación**:
   - Se renombra `firstname` a `first_name`
   - Se renombra `lastname` a `last_name`
   - Se renombra `hs_lead_status` a `lead_status`
   - Se crea el campo `full_name` combinando `firstname` y `lastname`
   - Se consulta la colección `lead_status` para obtener el `lead_status_id` correspondiente
3. **Upsert**: Se actualizan los leads en MongoDB por su `id`
4. **Agregación**: Se ejecuta un cálculo automático para contar leads por status

### Colecciones MongoDB utilizadas

- **`leads`**: Almacena los datos principales de leads
- **`lead_status`**: Tabla de referencia para mapear estados con IDs
- **`resume_lead_status`**: Resumen agregado con conteo de leads por status

### Resultado del agregado

Después del upsert de leads, se ejecuta automáticamente un agregado que:

- Agrupa los leads por `lead_status_id`
- Cuenta el total de leads en cada status
- Almacena el resultado en la colección `resume_lead_status`

## Procesamiento de Deals

### Transformaciones de campos

El script realiza las siguientes transformaciones en los datos de deals:

| Campo original | Campo transformado | Descripción                               |
| -------------- | ------------------ | ------------------------------------------ |
| `dealtype`   | `deal_type`      | Tipo de deal                               |
| `dealstage`  | `deal_stage`     | Etapa del deal                             |
| `dealname`   | `deal_name`      | Nombre del deal                            |
| `closedate`  | `close_date`     | Fecha de cierre (convertida a datetime)    |
| `createdate` | `create_date`    | Fecha de creación (convertida a datetime) |

### Proceso de datos

1. **Extracción**: Se obtienen los deals desde HubSpot
2. **Transformación**:
   - Se renombran los campos según la tabla anterior
   - Se convierten `close_date` y `create_date` de String a datetime
3. **Upsert**: Se actualizan los deals en MongoDB por su `id`
4. **Agregaciones**: Se ejecutan dos cálculos automáticos

### Colecciones MongoDB utilizadas

- **`deals`**: Almacena los datos principales de deals
- **`total_deals`**: Resumen agregado por stage de deal
- **`resume_close_deals`**: Resumen agregado por año/mes/stage

### Agregaciones automáticas

#### 1. Resumen por etapa (`total_deals`)

- Agrupa deals por `deal_stage`
- Calcula total de deals y suma de montos por etapa
- Upsert por `id` (deal_stage)

#### 2. Resumen por fecha de cierre (`resume_close_deals`)

- Agrupa deals por año, mes y `deal_stage` de `close_date`
- Calcula conteo y suma de montos
- Upsert por combinación de `year`, `month` y `deal_stage`

# 📋 Endpoints - API HubSpot Data

Port: 3000

## 💼 Deals (Negocios)

### `GET /deals`

## 👥 Leads (Contactos)

### `GET /leads`

## 📊 Resume Lead (Resumen de Leads)

### `GET /resume-lead`

## 💰 Resume Deals (Resumen de Negocios)

### `GET /resume-deals/total_deals`

### `GET /resume-deals/resume_close_deals`
