from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from jinja2 import Template
import uvicorn
import asyncio
import os
import json

PORT = 337  # Порт для фастапи

with open("assets/log_apps.json", "r", encoding="utf-8") as f:
    log_paths = json.load(f)


def create_app():
    app = FastAPI(title="FastAPI")

    @app.get("/{log_app}/tail")
    async def stream_log(log_app: str):
        file_path = log_paths.get(log_app)

        async def log_generator():
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
                for line in lines:
                    yield line + '<br>'
            with open(file_path, 'r', encoding='utf-8') as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline().rstrip()
                    if line:
                        yield line + '<br>'
                    else:
                        await asyncio.sleep(1)

        return StreamingResponse(log_generator(), media_type="text/html")

    @app.get("/{log_app}", response_class=HTMLResponse)
    async def get_log_viewer(log_app: str):
        with open("assets/log_template.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=Template(html_content).render(log_app=log_app))

    return app


app = create_app()


async def run():
    cnfg = uvicorn.Config(
        app="app.webserver:app",
        reload=True,
        port=PORT,
    )
    server = uvicorn.Server(cnfg)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(run())
