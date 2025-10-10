from kalibr.kalibr_app import KalibrApp

app = KalibrApp(title="Demo Kalibr App")

@app.action("hello", "Say hello")
def hello(name: str = "World"):
    return {"message": f"Hello, {name}!"}
