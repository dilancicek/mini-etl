from typer.testing import CliRunner
from mini_etl.cli import app

runner = CliRunner()

def test_cli_main_success(tmp_path):
    # Geçici test dosyalarımızı oluşturuyoruz
    input_file = tmp_path / "test_input.csv"
    input_file.write_text("id,name,age\n1,Test,25\n")
    
    output_file = tmp_path / "test_output.csv"
    dead_letter = tmp_path / "test_dead_letter.csv"

    # Komut satırı aracımızı sanki terminalden çalıştırıyormuş gibi çağırıyoruz
    result = runner.invoke(app, [
        "--input", str(input_file),
        "--output", str(output_file),
        "--dead-letter", str(dead_letter)
    ])

    # Beklenen sonuçları doğruluyoruz
    assert result.exit_code == 0
    assert "ETL süreci başlatılıyor" in result.stdout
    assert "İşlem Tamamlandı" in result.stdout

def test_cli_subcommand_early_return():
    # Alt komut (subcommand) çağrıldığında 'return' yapan if bloğunu test ediyoruz
    @app.command()
    def dummy_command():
        pass
        
    result = runner.invoke(app, ["--input", "a", "--output", "b", "dummy-command"])
    assert result.exit_code == 0