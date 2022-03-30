from main import app
import os
from dotenv import load_dotenv
load_dotenv()

app.debug = os.getenv("DEBUG", True)
app.run(host='0.0.0.0' , port=5001)

