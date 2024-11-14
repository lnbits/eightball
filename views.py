from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer
from lnbits.settings import settings
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse

from .crud import get_eightball

eightball_generic_router = APIRouter()


def eightball_renderer():
    return template_renderer(["eightball/templates"])


@eightball_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return eightball_renderer().TemplateResponse(
        "eightball/index.html", {"request": request, "user": user.json()}
    )


@eightball_generic_router.get("/{eightball_id}")
async def eightball(request: Request, eightball_id):
    eightball = await get_eightball(eightball_id)
    if not eightball:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )
    return eightball_renderer().TemplateResponse(
        "eightball/eightball.html",
        {
            "request": request,
            "eightball_id": eightball_id,
            "eightball_name": eightball.name,
            "eightball_description": eightball.description,
            "lnurlpay": eightball.lnurlpay(request),
            "web_manifest": f"/eightball/manifest/{eightball_id}.webmanifest",
        },
    )


@eightball_generic_router.get("/manifest/{eightball_id}.webmanifest")
async def manifest(eightball_id: str):
    eightball = await get_eightball(eightball_id)
    if not eightball:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )

    return {
        "short_name": settings.lnbits_site_title,
        "name": f"{eightball.name} - {settings.lnbits_site_title}",
        "icons": [
            {
                "src": (
                    settings.lnbits_custom_logo
                    if settings.lnbits_custom_logo
                    else "https://cdn.jsdelivr.net/gh/lnbits/lnbits@0.3.0/docs/logos/lnbits.png"
                ),
                "type": "image/png",
                "sizes": "900x900",
            }
        ],
        "start_url": f"/eightball/{eightball_id}",
        "background_color": "#1F2234",
        "description": "Minimal extension to build on",
        "display": "standalone",
        "scope": "/eightball/" + eightball_id,
        "theme_color": "#1F2234",
        "shortcuts": [
            {
                "name": f"{eightball.name} - {settings.lnbits_site_title}",
                "short_name": eightball.name,
                "description": f"{eightball.name} - {settings.lnbits_site_title}",
                "url": f"/eightball/{eightball_id}",
            }
        ],
    }
