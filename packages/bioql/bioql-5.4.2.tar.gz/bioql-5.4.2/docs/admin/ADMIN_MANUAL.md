# BioQL Admin Platform Manual
## Manual de Administración y Facturación v2.0.0

### 🎯 **Visión General**
La plataforma administrativa BioQL permite gestionar usuarios, API keys, facturación y monitoreo de uso para el SaaS de computación cuántica bioinformática.

---

## 📋 **Tabla de Contenidos**
1. [Acceso a la Plataforma](#acceso-a-la-plataforma)
2. [Gestión de Usuarios](#gestión-de-usuarios)
3. [Administración de API Keys](#administración-de-api-keys)
4. [Sistema de Facturación](#sistema-de-facturación)
5. [Monitoreo y Analytics](#monitoreo-y-analytics)
6. [Comandos de CLI Admin](#comandos-de-cli-admin)

---

## 🚀 **Acceso a la Plataforma**

### **Inicio del Sistema Administrativo**
```bash
# Navegar al directorio BioQL
cd /Users/heinzjungbluth/Desktop/bioql

# Opción 1: CLI Interactivo (Recomendado)
./bioql-admin-interactive

# Opción 2: Servidor Web (Puerto 5001)
/opt/homebrew/opt/python@3.11/bin/python3.11 bioql_auth_service.py

# Opción 3: Setup Inicial
./setup_admin_cli.sh
```

### **Credenciales de Acceso**
- **Base de Datos**: `/Users/heinzjungbluth/Desktop/bioql/bioql_billing.db`
- **Puerto Web**: `5001` (http://localhost:5001)
- **Admin CLI**: Acceso directo sin autenticación en entorno local

---

## 👥 **Gestión de Usuarios**

### **Crear Nuevo Usuario**
```bash
# CLI Interactivo
./bioql-admin-interactive
> 1. Create user
> Nombre: [Nombre del cliente]
> Email: [email@cliente.com]
> Plan: [free/pro/enterprise]
```

### **Estructura de Planes Disponibles**
| Plan | Precio | Shots/Mes | Características |
|------|--------|-----------|-----------------|
| **Free** | $0 | 1,000 | Solo simulador |
| **Pro** | $29 | 50,000 | Hardware cuántico real |
| **Enterprise** | $299 | Ilimitado | Soporte prioritario + DevKit |

### **Gestión de Estados de Usuario**
```sql
-- Activar usuario
UPDATE users SET is_active = 1 WHERE email = 'user@example.com';

-- Desactivar usuario
UPDATE users SET is_active = 0 WHERE email = 'user@example.com';

-- Cambiar plan
UPDATE users SET current_plan = 'pro' WHERE email = 'user@example.com';
```

---

## 🔑 **Administración de API Keys**

### **Generar API Key para Usuario**
```bash
./bioql-admin-interactive
> 2. Generate API key
> User ID: [user_id from database]
> Description: [Descripción opcional]
```

### **Estructura de API Keys**
- **Formato**: `bioql_[random_string]`
- **Longitud**: 32 caracteres
- **Hash Storage**: SHA256 en base de datos
- **Estados**: Active/Inactive

### **Gestión de API Keys**
```sql
-- Ver API keys de un usuario
SELECT ak.id, ak.key_prefix, ak.description, ak.created_at, ak.is_active
FROM api_keys ak
JOIN users u ON ak.user_id = u.id
WHERE u.email = 'user@example.com';

-- Desactivar API key
UPDATE api_keys SET is_active = 0 WHERE id = [api_key_id];

-- Generar nueva API key
INSERT INTO api_keys (id, user_id, key_hash, key_prefix, description, is_active)
VALUES (UUID(), [user_id], SHA256('[new_key]'), 'bioql_xxx', 'Description', 1);
```

---

## 💰 **Sistema de Facturación**

### **Estructura de Costos**
```python
# Costos por Backend
BACKEND_COSTS = {
    'simulator': 0.001,    # $0.001 por shot
    'aer': 0.001,         # $0.001 por shot
    'ibm_*': 0.01,        # $0.01 por shot
    'ionq_*': 0.02        # $0.02 por shot
}

# Multiplicadores de Complejidad
COMPLEXITY_MULTIPLIERS = {
    '2_qubits': 1.0,
    '4_qubits': 1.5,
    '6_qubits': 2.0,
    '8_qubits': 3.0,
    '10+_qubits': 5.0
}

# Multiplicadores de Algoritmo
ALGORITHM_MULTIPLIERS = {
    'basic': 1.0,
    'bell': 1.0,
    'qft': 1.5,
    'grover': 2.0,
    'vqe': 2.5,
    'qaoa': 2.5,
    'shor': 3.0,
    'docking': 2.0,     # DevKit feature
    'alignment': 1.8    # DevKit feature
}
```

### **Consultas de Facturación**
```sql
-- Uso mensual por usuario
SELECT u.email,
       COUNT(*) as total_executions,
       SUM(ul.shots_executed) as total_shots,
       SUM(CAST(ul.total_cost AS DECIMAL)) as total_cost
FROM usage_logs ul
JOIN users u ON ul.user_id = u.id
WHERE ul.created_at >= date('now', '-1 month')
GROUP BY u.id;

-- Top 10 usuarios por costo
SELECT u.email, u.current_plan,
       SUM(CAST(ul.total_cost AS DECIMAL)) as monthly_revenue
FROM usage_logs ul
JOIN users u ON ul.user_id = u.id
WHERE ul.created_at >= date('now', '-1 month')
GROUP BY u.id
ORDER BY monthly_revenue DESC
LIMIT 10;

-- Análisis de algoritmos más usados
SELECT ul.algorithm_type,
       COUNT(*) as usage_count,
       AVG(CAST(ul.total_cost AS DECIMAL)) as avg_cost
FROM usage_logs ul
WHERE ul.created_at >= date('now', '-1 month')
GROUP BY ul.algorithm_type
ORDER BY usage_count DESC;
```

### **Reportes de Facturación**
```bash
# Generar reporte mensual
./bioql-admin-interactive
> 4. View reports
> Monthly revenue report
> Export to CSV: Y/N

# Reporte de uso por backend
SELECT backend_used, COUNT(*), SUM(shots_executed)
FROM usage_logs
WHERE created_at >= date('now', '-1 month')
GROUP BY backend_used;
```

---

## 📊 **Monitoreo y Analytics**

### **Métricas Clave**
```sql
-- Usuarios activos (último mes)
SELECT COUNT(DISTINCT user_id) as active_users
FROM usage_logs
WHERE created_at >= date('now', '-1 month');

-- Revenue mensual
SELECT SUM(CAST(total_cost AS DECIMAL)) as monthly_revenue
FROM usage_logs
WHERE created_at >= date('now', '-1 month');

-- Distribución por plan
SELECT current_plan, COUNT(*) as user_count
FROM users
WHERE is_active = 1
GROUP BY current_plan;

-- Ejecuciones por día (últimos 30 días)
SELECT date(created_at) as execution_date,
       COUNT(*) as daily_executions,
       SUM(shots_executed) as daily_shots
FROM usage_logs
WHERE created_at >= date('now', '-30 days')
GROUP BY date(created_at)
ORDER BY execution_date;
```

### **Alertas y Límites**
```sql
-- Usuarios cerca del límite (>80% del plan)
SELECT u.email, u.current_plan,
       SUM(ul.shots_executed) as shots_used,
       CASE u.current_plan
           WHEN 'free' THEN 1000
           WHEN 'pro' THEN 50000
           WHEN 'enterprise' THEN 999999999
       END as plan_limit
FROM users u
JOIN usage_logs ul ON u.id = ul.user_id
WHERE ul.created_at >= date('now', '-1 month')
GROUP BY u.id
HAVING shots_used > (plan_limit * 0.8);

-- Usuarios que excedieron límites
SELECT u.email, u.current_plan,
       SUM(ul.shots_executed) as shots_used
FROM users u
JOIN usage_logs ul ON u.id = ul.user_id
WHERE ul.created_at >= date('now', '-1 month')
  AND u.current_plan = 'free'
GROUP BY u.id
HAVING shots_used > 1000;
```

---

## 🛠 **Comandos de CLI Admin**

### **Comandos Principales**
```bash
# Iniciar CLI administrativo
./bioql-admin-interactive

# Comandos disponibles:
1. Create user                    # Crear nuevo usuario
2. Generate API key              # Generar API key
3. View user details            # Ver detalles de usuario
4. View reports                 # Ver reportes de uso
5. Database operations          # Operaciones de BD
6. Export data                  # Exportar datos
7. System health check          # Verificar sistema
8. Billing operations           # Operaciones de facturación
9. API key management           # Gestión de API keys
0. Exit                         # Salir
```

### **Operaciones de Base de Datos**
```bash
# Backup de base de datos
cp bioql_billing.db bioql_billing_backup_$(date +%Y%m%d).db

# Verificar integridad
sqlite3 bioql_billing.db "PRAGMA integrity_check;"

# Vacuum (optimizar)
sqlite3 bioql_billing.db "VACUUM;"

# Estadísticas de tablas
sqlite3 bioql_billing.db "SELECT name, COUNT(*) FROM sqlite_master sm
JOIN pragma_table_info(sm.name) pti
WHERE sm.type='table'
GROUP BY sm.name;"
```

### **Scripts de Mantenimiento**
```bash
# Limpiar logs antiguos (>6 meses)
sqlite3 bioql_billing.db "DELETE FROM usage_logs
WHERE created_at < date('now', '-6 months');"

# Estadísticas de rendimiento
sqlite3 bioql_billing.db "SELECT
    COUNT(*) as total_executions,
    AVG(execution_time) as avg_execution_time,
    MAX(execution_time) as max_execution_time
FROM usage_logs
WHERE created_at >= date('now', '-1 month');"
```

---

## 🔧 **Troubleshooting**

### **Problemas Comunes**

#### **1. Base de datos no accesible**
```bash
# Verificar permisos
ls -la bioql_billing.db
chmod 664 bioql_billing.db

# Verificar proceso
ps aux | grep bioql
```

#### **2. API keys no funcionan**
```sql
-- Verificar API key
SELECT ak.*, u.email, u.is_active as user_active
FROM api_keys ak
JOIN users u ON ak.user_id = u.id
WHERE ak.key_hash = SHA256('bioql_key_to_check');
```

#### **3. Facturación incorrecta**
```sql
-- Recalcular costos
UPDATE usage_logs
SET total_cost = (
    shots_executed *
    base_cost_per_shot *
    complexity_multiplier *
    algorithm_multiplier
)
WHERE created_at >= date('now', '-1 day');
```

#### **4. Performance lenta**
```sql
-- Crear índices si no existen
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_date
ON usage_logs(user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_usage_logs_date
ON usage_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_api_keys_hash
ON api_keys(key_hash);
```

---

## 📞 **Soporte y Contacto**

- **Email Técnico**: hello@spectrixrd.com
- **Documentación**: https://docs.bioql.com
- **GitHub Issues**: https://github.com/bioql/bioql/issues
- **Emergency Contact**: Admin CLI → Option 7 (System health check)

---

## 🔐 **Seguridad**

### **Mejores Prácticas**
1. **Backup regular** de `bioql_billing.db`
2. **Monitoreo de logs** para actividad sospechosa
3. **Rotación de API keys** cada 6 meses
4. **Auditoría mensual** de usuarios activos
5. **Verificación de límites** semanalmente

### **Logs de Seguridad**
```sql
-- Actividad reciente por usuario
SELECT u.email, ul.created_at, ul.algorithm_type, ul.backend_used
FROM usage_logs ul
JOIN users u ON ul.user_id = u.id
WHERE ul.created_at >= datetime('now', '-24 hours')
ORDER BY ul.created_at DESC;

-- API keys comprometidas (uso excesivo)
SELECT u.email, ak.key_prefix, COUNT(*) as usage_count
FROM usage_logs ul
JOIN api_keys ak ON ul.api_key_id = ak.id
JOIN users u ON ak.user_id = u.id
WHERE ul.created_at >= datetime('now', '-1 hour')
GROUP BY ak.id
HAVING usage_count > 100;
```

---

**© 2024 SpectrixRD - BioQL Admin Platform**
*Manual actualizado para BioQL v2.0.0 con DevKit capabilities*