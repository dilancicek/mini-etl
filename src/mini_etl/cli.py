import typer
from pathlib import Path
from mini_etl.sources import CSVSource
from mini_etl.sinks import CSVSink
from mini_etl.engine import ETLEngine

app = typer.Typer(help="Mini-ETL Komut Satırı Aracı")

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_file: Path = typer.Option(..., "--input", "-i", help="Girdi CSV dosyası"),
    output_file: Path = typer.Option(..., "--output", "-o", help="Çıktı CSV dosyası"),
    dead_letter: Path = typer.Option(Path("dead_letter.csv"), "--dead-letter", "-d", help="Hatalı satırlar dosyası")
):
    """Mini-ETL boru hattını çalıştırır."""
    if ctx.invoked_subcommand is not None:
        return

    typer.echo(f"ETL süreci başlatılıyor: {input_file} -> {output_file}")
    
    source = CSVSource(file_path=input_file)
    sink = CSVSink(file_path=output_file, fieldnames=["id", "name", "age"])
    
    engine = ETLEngine(
        source=source,
        pipeline=None,
        sink=sink,
        dead_letter_path=dead_letter
    )
    
    summary = engine.run()
    typer.echo(f"İşlem Tamamlandı! Özet: {summary}")

if __name__ == "__main__":
    app()