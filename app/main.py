import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from app.api.routes.diseases_route import diseases_router
from app.api.routes.symptoms_route import symptoms_router


def create_app():
    app = FastAPI(
        title="Health tracker",
        description="Health tracker Application",
        version="1.0.0",
    )

    app.include_router(symptoms_router)
    app.include_router(diseases_router)

    app.add_exception_handler(RequestValidationError, lambda request, exc: JSONResponse(
        status_code=400,
        content={"error": exc.errors()},
    ))

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
