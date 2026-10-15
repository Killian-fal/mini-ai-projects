import os

import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


def main():
    load_dotenv()
    from interactive_support_core.registry import check_flows
    from interactive_support_core.translation import check_translations
    from interactive_support_observability import init_observability
    from .app import app

    init_observability()
    check_translations()
    check_flows()
    # TODO: rework mais c'est pour demo
    uvicorn.run(
        CORSMiddleware(
            app, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
        ),
        port=int(os.environ.get("API_PORT", "8000")),
    )
