from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# static 디렉토리 생성
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory="templates")

def init_saml_auth(req):
    saml_settings = {
        "strict": True,
        "debug": os.getenv('APP_DEBUG', 'True').lower() == 'true',
        "sp": {
            "entityId": os.getenv('SAML_SP_ENTITY_ID'),
            "assertionConsumerService": {
                "url": os.getenv('SAML_SP_ACS_URL'),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            }
        },
        "idp": {
            "entityId": os.getenv('SAML_IDP_ENTITY_ID'),
            "singleSignOnService": {
                "url": os.getenv('SAML_IDP_SSO_URL'),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": os.getenv('SAML_IDP_X509_CERT')
        }
    }
    return OneLogin_Saml2_Auth(req, saml_settings)

async def prepare_request(request: Request):
    form_data = await request.form()
    return {
        'https': 'on' if request.url.scheme == 'https' else 'off',
        'http_host': request.headers.get('host', ''),
        'script_name': request.url.path,
        'server_port': request.url.port or (443 if request.url.scheme == 'https' else 80),
        'get_data': request.query_params,
        'post_data': form_data,
        'query_string': request.url.query
    }

@app.get("/")
async def home(request: Request):
    req = await prepare_request(request)
    auth = init_saml_auth(req)
    
    # 이미 인증된 세션이 있는지 확인
    if auth.is_authenticated():
        return RedirectResponse(os.getenv('TARGET_REDIRECT_URL'), status_code=303)
    
    # 인증되지 않은 경우 자동으로 SAML 로그인 시작
    return RedirectResponse(auth.login())

@app.post("/acs")
async def acs(request: Request):
    req = await prepare_request(request)
    auth = init_saml_auth(req)
    auth.process_response()
    errors = auth.get_errors()
    
    if not errors:
        if auth.is_authenticated():
            return RedirectResponse(os.getenv('TARGET_REDIRECT_URL'), status_code=303)
    
    raise HTTPException(status_code=401, detail=', '.join(errors))
