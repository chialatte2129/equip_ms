from main import app
import os

app.debug = os.getenv("DEBUG", True)
app.run()