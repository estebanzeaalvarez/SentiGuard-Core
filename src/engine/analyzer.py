import sqlite3
import datetime
import os
import json
import requests

class SentimentAnalyzer:
    def __init__(self):
        # 1. Localización robusta de la raíz del proyecto (3 niveles arriba)
        self.ruta_raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.ruta_config = os.path.join(self.ruta_raiz, "config.json")
        self.db_name = os.path.join(self.ruta_raiz, "sentiguard.db")
        
        # 2. Carga segura de configuración
        if not os.path.exists(self.ruta_config):
            raise FileNotFoundError(f"CRÍTICO: No se encontró config.json en {self.ruta_config}")

        with open(self.ruta_config, "r") as f:
            self.config = json.load(f)
        
        # 3. URL mandatoria solicitada por el Router de Hugging Face
        self.api_url = "https://router.huggingface.co/hf-inference/models/cardiffnlp/twitter-xlm-roberta-base-sentiment"
        token = self.config.get('hf_token', '').strip()
        self.headers = {"Authorization": f"Bearer {token}"}
        
        self._preparar_base_de_datos()
        print(f"DEBUG: Configuración cargada desde {self.ruta_config}")    

    def _preparar_base_de_datos(self):
        """Crea la tabla base."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alertas (
                    id TEXT PRIMARY KEY,
                    fecha TEXT,
                    usuario TEXT,
                    texto TEXT,
                    score REAL,
                    label TEXT
                )
            ''')
            conn.commit()

    def analizar(self, texto: str):
        """Envía el texto a la IA y mapea los resultados con alta precisión."""
        texto_limpio = texto.replace('"', '').replace("'", "")[:400]
        payload = {"inputs": texto_limpio, "options": {"wait_for_model": True}}
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                res_json = response.json()
                
                if isinstance(res_json, list) and len(res_json) > 0:
                    datos = res_json[0] if isinstance(res_json[0], list) else res_json
                    mejor = max(datos, key=lambda x: x['score'])
                    label_ia = mejor['label'].lower()
                    score_ia = mejor['score']
                    
                    if "positive" in label_ia or "label_2" in label_ia: 
                        sentimiento = "POSITIVO"
                    elif "negative" in label_ia or "label_0" in label_ia: 
                        sentimiento = "NEGATIVO"
                    else: 
                        sentimiento = "NEUTRAL"
                    
                    return {"label": sentimiento, "score": float(score_ia)}
            
            print(f"⚠️ API Error {response.status_code}: {response.text}")
            return {"label": "NEUTRAL", "score": 0.0}
            
        except Exception as e:
            print(f"❌ FALLO CRÍTICO IA: {e}")
            return {"label": "NEUTRAL", "score": 0.0}

    def obtener_historial_ids(self):
        """Obtiene IDs previos para evitar duplicados."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM alertas')
            return {fila[0] for fila in cursor.fetchall()}

    def registrar_alerta(self, usuario, texto, score, sentimiento="NEUTRAL", notificar=True):
        """Guarda en DB y notifica a Discord con debug de respuesta."""
        id_alerta = f"{usuario}_{texto[:100]}" 
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO alertas VALUES (?, ?, ?, ?, ?, ?)', 
                             (id_alerta, fecha, usuario, texto, score, sentimiento))
                conn.commit()
            
            webhook_url = self.config.get("discord_webhook")
            es_critico = (sentimiento == "NEGATIVO") or (score == 0.0)
            
            if webhook_url and es_critico and notificar:
                payload = {
                    "embeds": [{
                        "title": "🚨 NOTIFICACIÓN SENTIGUARD",
                        "description": f"**Contenido:** {texto[:500]}",
                        "color": 15158332 if sentimiento == "NEGATIVO" else 8421504,
                        "fields": [
                            {"name": "Estado", "value": "⚠️ FALLO IA" if score == 0.0 else sentimiento, "inline": True},
                            {"name": "Confianza", "value": f"{score:.2%}", "inline": True}
                        ],
                        "footer": {"text": "SentiGuard Core"}
                    }]
                }
                r = requests.post(webhook_url, json=payload, timeout=5)
                if r.status_code == 204:
                    print(f"✅ Discord: Alerta enviada para {usuario}")
                else:
                    print(f"❌ Discord Error {r.status_code}: {r.text}")
                    
        except Exception as e:
            print(f"[!] Error al registrar alerta: {e}")