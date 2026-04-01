import feedparser

class RedditScanner:
    def __init__(self, feeds: list = None):
        """
        Clase encargada de la ingesta de datos vía RSS.
        Permite inyectar una lista de feeds o usar los de seguridad por defecto.
        """
        self.feeds = feeds or [
            "https://www.wired.com/feed/category/security/latest/rss",
            "https://www.theverge.com/rss/index.xml"
        ]

    def conectar(self) -> bool:
        """Valida que haya feeds configurados para escanear."""
        return len(self.feeds) > 0

    def obtener_posts(self, limite: int = 10) -> list:
        """
        Extrae titulares y metadatos de los feeds configurados.
        Retorna una lista de diccionarios con la estructura requerida por el core.
        """
        posts_reales = []
        
        for url in self.feeds:
            try:
                feed = feedparser.parse(url)
                
                # Manejo de error de parseo (bozo bit)
                if feed.bozo:
                    continue

                for entry in feed.entries[:limite]:
                    # Extraemos el nombre de la fuente dinámicamente desde la URL
                    fuente = "Wired" if "wired" in url.lower() else "The Verge"
                    
                    posts_reales.append({
                        "titulo": entry.get("title", "Sin título"),
                        "autor": fuente,
                        "link": entry.get("link", "") # Crítico para evitar duplicados en DB
                    })
            except Exception as e:
                print(f"[!] Error crítico en ingesta desde {url}: {e}")
        
        return posts_reales