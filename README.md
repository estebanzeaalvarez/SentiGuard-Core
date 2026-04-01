# 🛡️ SentiGuard Core v1.2
**Real-Time Sentiment Intelligence & Threat Monitoring System**

SentiGuard es un ecosistema de monitorización automatizada que utiliza Inteligencia Artificial para analizar el flujo de noticias y redes sociales, detectando crisis de reputación o amenazas en tiempo real.

---

## 🚀 Arquitectura Técnica
El sistema está diseñado bajo una arquitectura desacoplada para garantizar escalabilidad y eficiencia:

* **Ingestion Engine:** Scrapers optimizados que consumen fuentes de datos (Reddit/News APIs).
* **AI Analysis (NLP):** Integración con modelos de lenguaje de Hugging Face para clasificación de sentimiento.
* **Data Persistence:** Base de datos SQLite con lógica de deduplicación de incidentes.
* **Alerting System:** Notificaciones instantáneas vía Webhooks de Discord.
* **Command Center:** Dashboard interactivo desarrollado en Streamlit con visualizaciones de Plotly.

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.10+
* **IA:** Transformers (Hugging Face), Pipeline de Análisis de Sentimiento.
* **Visualización:** Streamlit, Plotly Express, Rich (Terminal UI).
* **Backend:** SQLite, Pandas, Subprocess Management.

## 📈 Impacto de Negocio
Este proyecto resuelve el problema de la latencia en la comunicación de crisis. Permite a departamentos de Relaciones Públicas o CEOs reaccionar a menciones negativas antes de que se vuelvan virales, reduciendo el riesgo reputacional.

## 📦 Instalación y Uso
1. Clonar el repositorio.
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar `config.json` con tus credenciales.
4. Ejecutar el monitor: `python main.py`
5. Lanzar el dashboard: `streamlit run dashboard.py`