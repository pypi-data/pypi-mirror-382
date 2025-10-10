import typer
import subprocess

app = typer.Typer(help="Kalibr Connect - integrate your app with any AI model instantly.")

@app.command("serve")
def serve_app(file: str):
    """Run a Kalibr app locally."""
    typer.echo(f"🚀 Serving {file} locally...")
    subprocess.run(["uvicorn", f"{file.replace('.py','')}:app", "--reload"])

@app.command("deploy")
def deploy_app(file: str):
    """Deploy your Kalibr app (placeholder for future)."""
    typer.echo(f"🚀 Deploying {file} (not yet implemented).")

@app.command("usage")
def usage():
    """Show Kalibr Connect usage info."""
    typer.echo("\nKalibr Connect Commands:")
    typer.echo("  kalibr-connect serve <file>   Run a Kalibr app locally.")
    typer.echo("  kalibr-connect deploy <file>  Deploy your Kalibr app.")
    typer.echo("  kalibr-connect usage          Show this usage guide.\n")

def main():
    app()

if __name__ == "__main__":
    main()
