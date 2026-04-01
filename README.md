# 🛡️ SentiGuard Core v1.2
**Real-Time Sentiment Intelligence & Threat Monitoring System**

SentiGuard es un ecosistema de monitorización automatizada que utiliza Inteligencia Artificial para analizar el flujo de noticias y redes sociales, detectando crisis de reputación o amenazas en tiempo real.

---

## 🌐 Dashboard en Vivo
Puedes acceder a la interfaz de monitoreo en tiempo real a través del siguiente enlace:
> **Link:** [SentiGuard Command Center](https://sentiguard-core-fmdtzpxpwkzgsspsy4dqka.streamlit.app/)

---

## 🏗️ Arquitectura Técnica
El sistema está diseñado bajo una arquitectura desacoplada para garantizar escalabilidad y eficiencia:

* **Ingestion Engine:** Scrapers optimizados que consumen fuentes de datos (Reddit/News APIs).
* **AI Analysis (NLP):** Integración con modelos de lenguaje de Hugging Face para clasificación de sentimiento.
* **Data Persistence:** Base de datos SQLite con lógica de deduplicación de incidentes.
* **Alerting System:** Notificaciones instantáneas vía Webhooks de Discord.
* **Command Center:** Dashboard interactivo desarrollado en Streamlit con visualizaciones de Plotly.

## 💻 Tecnologías Utilizadas
* **Lenguaje:** Python 3.10+
* **IA:** Transformers (Hugging Face), Pipeline de Análisis de Sentimiento.
* **Visualización:** Streamlit, Plotly Express, Rich (Terminal UI).
* **Backend:** SQLite, Pandas, Subprocess Management.

## 📊 Impacto de Negocio
Este proyecto resuelve el problema de la latencia en la comunicación de crisis. Permite a departamentos de Relaciones Públicas o CEOs reaccionar a menciones negativas antes de que se vuelvan virales, reduciendo el riesgo reputacional.

## ⚙️ Implementación y Operación (System Overview)
El despliegue sigue estándares de grado industrial para garantizar la integridad del análisis y la seguridad de los datos.

### Configuración del Entorno
* **Aislamiento:** Uso de `virtualenv` para gestionar dependencias específicas y asegurar la reproducibilidad del pipeline.
* **DevSecOps:** Las credenciales de APIs y Webhooks se gestionan mediante `config.json` (fuera del control de versiones) para proteger la integridad de las fuentes.

### Pipeline de Ejecución
1. **Initial Boot:** Validación de integridad de la base de datos local y esquemas.
2. **Ingestion Cycle:** Activación de scrapers multihilo diseñados para optimizar el throughput de datos.
3. **Inference Stage:** Procesamiento y clasificación de texto mediante modelos de lenguaje.
4. **Broadcast:** Despacho de alertas y actualización del dashboard visual.