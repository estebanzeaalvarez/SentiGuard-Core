import time
import json
import sys
from src.engine.analyzer import SentimentAnalyzer
from src.ingestion.reddit_client import RedditScanner
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def generar_tabla(resultados):
    table = Table(title="[bold blue]Monitor de Sentimiento en Tiempo Real[/bold blue]", expand=True)
    table.add_column("Fuente", style="cyan", no_wrap=True)
    table.add_column("Titular", style="white")
    table.add_column("Sentimiento", justify="center")
    table.add_column("Score", justify="right")

    for res in resultados:
        colores = {"POSITIVO": "green", "NEGATIVO": "red", "NEUTRAL": "yellow"}
        color = colores.get(res['label'], "white")
        table.add_row(res['autor'], res['titulo'], f"[{color}]{res['label']}[/{color}]", f"{res['score']:.2f}")
    return table

def iniciar_sistema():
    # 1. Cargar Configuración
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {"frecuencia_escaneo": 10}
    
    frecuencia = config.get("frecuencia_escaneo", 10)
    resultados = []
    primera_corrida = True 

    # 2. Inicializar Componentes
    console.clear()
    console.print(Panel.fit(" [bold cyan]SentiGuard Core v1.2[/bold cyan] \n [italic]Modo Vigilante Activo[/italic] ", border_style="blue"))

    analyzer = SentimentAnalyzer()
    scanner = RedditScanner()
    
    console.print("[yellow]i[/yellow] Cargando historial de alertas...")
    alertados = analyzer.obtener_historial_ids()
    console.print(f"[green]✓[/green] {len(alertados)} alertas previas cargadas.\n")
    time.sleep(1)

    # 3. Bucle de Ejecución
    try:
        solo_una_vez = "--once" in sys.argv

        while True:
            # Obtenemos datos del scanner (Wired + Verge)
            posts = scanner.obtener_posts(limite=5) 
            resultados = []
            
            for p in posts:
                titulo = p['titulo']
                link = p['link']
                autor = p['autor']
                
                # Análisis de sentimiento vía IA
                sentimiento = analyzer.analizar(titulo)
                
# Solo registramos si el link es nuevo
                if link not in alertados:
                    # Forzamos notificar=True para probar el Webhook inmediatamente
                    analyzer.registrar_alerta(
                        usuario=autor, 
                        texto=titulo, 
                        score=sentimiento['score'], 
                        sentimiento=sentimiento['label'], 
                        notificar=True
                    )
                    alertados.add(link)
                
                resultados.append({
                    "autor": autor, "titulo": titulo,
                    "label": sentimiento['label'], "score": sentimiento['score']
                })
                
                # Pausa para evitar Rate Limit de la API
                time.sleep(1)

            primera_corrida = False
            console.clear()
            console.print(generar_tabla(resultados))
            
            if solo_una_vez:
                console.print("[green]✓[/green] Escaneo ráfaga finalizado.")
                break 

            console.print(f"\n[dim]Actualización: {time.strftime('%H:%M:%S')} | Total DB: {len(alertados)}[/dim]")
            time.sleep(frecuencia)
            
    except KeyboardInterrupt:
        console.print("\n" + "─" * 50)
        console.print("[bold red]⚠ Sistema detenido por el usuario.[/bold red]")
        
        if resultados:
            total = len(resultados)
            negativos = sum(1 for r in resultados if r['label'] == "NEGATIVO")
            positivos = sum(1 for r in resultados if r['label'] == "POSITIVO")
            promedio = sum(r['score'] for r in resultados) / total
            
            reporte = Table.grid(padding=1)
            reporte.add_column(style="bold cyan")
            reporte.add_column()
            reporte.add_row("Total analizados:", f"{total}")
            reporte.add_row("Sentimientos Negativos:", f"[red]{negativos}[/red]")
            reporte.add_row("Sentimientos Positivos:", f"[green]{positivos}[/green]")
            reporte.add_row("Clima detectado:", f"{'Sano' if promedio > 0.5 else 'Tenso o Crítico'}")
            
            console.print(Panel(reporte, title="[bold white]Reporte de Sesión Final[/bold white]", border_style="green"))

if __name__ == "__main__":
    iniciar_sistema()