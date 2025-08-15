from typing import Optional
import os
import httpx
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Папка с шаблонами
templates = Jinja2Templates(directory="app/presentation/web/templates")

router = APIRouter(prefix="/web", tags=["web"])

# Базовый URL JSON-API (если роуты в том же приложении — localhost:8080)
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8080")

async def _get_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get("access_token")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Если есть токен — в кабинет, иначе на логин
    token = _get_token_from_cookie(request)
    if token:
        return RedirectResponse(url="/web/dashboard", status_code=302)
    return RedirectResponse(url="/web/login", status_code=302)

# ---------- Аутентификация ----------
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    # Подстрой пути под свой роут авторизации, если он отличается
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10.0) as client:
        resp = await client.post("/auth/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные данные"}, status_code=400)
    data = resp.json()
    token = data.get("access_token")
    if not token:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Не получен токен"}, status_code=400)

    r = RedirectResponse(url="/web/dashboard", status_code=302)
    # httponly, чтобы JS не трогал токен
    r.set_cookie("access_token", token, httponly=True, secure=False)  # secure=True в проде на HTTPS
    return r

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register")
async def register_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10.0) as client:
        resp = await client.post("/auth/register", json={"email": email, "password": password})
    if resp.status_code != 201 and resp.status_code != 200:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Регистрация не удалась"}, status_code=400)
    # после регистрации сразу логинимся
    return await login_submit(request, email=email, password=password)

@router.get("/logout")
async def logout():
    r = RedirectResponse(url="/web/login", status_code=302)
    r.delete_cookie("access_token")
    return r

# ---------- Кабинет / перевод / история / кошелёк ----------
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = _get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/web/login", status_code=302)

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10.0, headers=headers) as client:
        # подстрой пути под свои роуты, если отличаются
        balance_resp = await client.get("/wallet/balance")
        hist_resp = await client.get("/history")

    balance = balance_resp.json().get("balance") if balance_resp.status_code == 200 else "—"
    history = hist_resp.json() if hist_resp.status_code == 200 else []

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "balance": balance, "history": history, "error": None, "result": None},
    )

@router.post("/translate", response_class=HTMLResponse)
async def translate_submit(request: Request, text: str = Form(...), target_lang: str = Form("en")):
    token = _get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/web/login", status_code=302)

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"text": text, "target_lang": target_lang}  # подстрой под свой /translate
    async with httpx.AsyncClient(base_url=API_BASE, timeout=20.0, headers=headers) as client:
        resp = await client.post("/translate", json=payload)

        balance_resp = await client.get("/wallet/balance")
        hist_resp = await client.get("/history")

    result = resp.json().get("translated_text") if resp.status_code == 200 else None
    balance = balance_resp.json().get("balance") if balance_resp.status_code == 200 else "—"
    history = hist_resp.json() if hist_resp.status_code == 200 else []
    error = None if result else "Ошибка перевода"

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "balance": balance, "history": history, "error": error, "result": result},
    )

@router.post("/topup", response_class=HTMLResponse)
async def topup_submit(request: Request, amount: float = Form(...)):
    token = _get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/web/login", status_code=302)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10.0, headers=headers) as client:
        resp = await client.post("/wallet/topup", json={"amount": amount})

        balance_resp = await client.get("/wallet/balance")
        hist_resp = await client.get("/history")

    ok = resp.status_code in (200, 201)
    balance = balance_resp.json().get("balance") if balance_resp.status_code == 200 else "—"
    history = hist_resp.json() if hist_resp.status_code == 200 else []
    error = None if ok else "Пополнение не удалось"

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "balance": balance, "history": history, "error": error, "result": None},
    )
