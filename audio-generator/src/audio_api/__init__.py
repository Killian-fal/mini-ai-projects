import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()


def run():
    from audio_api.app import create_app

    app = create_app()

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run()
