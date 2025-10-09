import contextlib
import os

from fastapi import FastAPI, Query, responses
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from shipaw.config import ShipawSettings
from shipaw.fapi.alerts import Alert, AlertType, Alerts
from shipaw.fapi.routes_api import router as json_router
from shipaw.fapi.routes_html import router as html_router


@contextlib.asynccontextmanager
async def lifespan(app_: FastAPI):
    try:
        # app_.settings = ShipawSettings.from_env()
        # set_pf_env()
        # pythoncom.CoInitialize()
        # with sqm.Session(am_db.ENGINE) as session:
        #     pf_shipper = ELClient()
        #     populate_db_from_cmc(session, pf_shipper)
        yield

    finally:
        # pythoncom.CoUninitialize()

        ...


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=str(ShipawSettings.from_env().static_dir)), name='static')
app.include_router(json_router, prefix='/api')
app.include_router(html_router)
app.ship_live = ShipawSettings.from_env().shipper_live
app.alerts = Alerts.empty()


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg2 = ''
    for err in errors:
        if type := err.get('type'):
            msg2 += type + ' '
        if loc := err.get('loc'):
            msg2 += f'in {loc} '
        if ctx := err.get('ctx'):
            if reason := ctx.get('reason'):
                msg2 += f': {reason} '
        if input_ := err.get('input'):
            msg2 += f'. Input = {input_} '

    logger.error(msg2)
    alerts = Alerts(alert=[Alert(code=1, message=msg2, type=AlertType.ERROR)])
    return JSONResponse(
        status_code=422,
        content={'detail': jsonable_encoder(exc.errors()), 'alerts': alerts.model_dump(mode='json'), 'message': msg2},
    )


@app.get('/robots.txt', response_class=responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', include_in_schema=False)
async def favicon_ico():
    return responses.RedirectResponse(url='/static/favicon.svg')


@app.get('/', response_class=JSONResponse)
async def base():
    return JSONResponse(content={'status': 'ok'})


@app.get('/open-file', response_class=HTMLResponse)
async def open_file(filepath: str = Query(...)):
    os.startfile(filepath)
    return HTMLResponse(content=f'<span>Re</span>')

