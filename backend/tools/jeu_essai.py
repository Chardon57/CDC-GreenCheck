"""Jeu d'essai de GreenCheck : scénario complet exécuté sur le vrai code du back-end.

Ce qui est RÉEL : routes FastAPI, authentification (Argon2id, JWT), validation, traitement des
images (Pillow), accès aux données (SQLAlchemy), stockage des photos sur disque.
Ce qui est SIMULÉ : la base (SQLite en mémoire au lieu de MariaDB), Pl@ntNet et le moteur IA
(réponses prédéfinies), le dossier de stockage (dossier temporaire).

Usage (depuis le dossier backend/, dépendances installées) :  python tools/jeu_essai.py
"""
import os, sys, io, json, tempfile, pathlib
BACKEND = pathlib.Path(__file__).resolve().parents[1]
os.environ.update(DB_USER="essai",DB_PASSWORD="essai",JWT_SECRET_KEY="cle-de-jeu-d-essai-longue-de-plus-de-32-octets",JWT_ALGORITHM="HS256",JWT_EXPIRE_MINUTES="30",PLANTNET_API_KEY="cle-factice",ENGINE_URL="http://moteur.test:8001")
sys.path.insert(0, str(BACKEND)); os.chdir(BACKEND)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from PIL import Image
import models
from config.database import Base, db
from config import storage
from main import app
from services import analysis_service
from services.plantnet_service import PlantIdentification, PlantNotRecognizedError
from services.diagnosis_service import PlantDiagnosis, DiagnosisUnavailableError
from models.disease import Disease; from models.treatment import Treatment; from models.result import Result

tmp=pathlib.Path(tempfile.mkdtemp()); storage.UPLOADS_DIR=tmp/"uploads"
eng=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool); Base.metadata.create_all(eng)
SF=sessionmaker(bind=eng)
def ov():
    with SF() as s: yield s
app.dependency_overrides[db.get_session]=ov
with SF() as s:
    d=Disease(name="Oïdium",treatments=[Treatment(advice="Retirer les feuilles atteintes.")]); s.add(Result(label="Malade",disease=d)); s.commit()
state={"ident":PlantIdentification("Monstera","Monstera deliciosa",0.73,"Araceae"),"diag":PlantDiagnosis("Oïdium",0.69),"ierr":None,"derr":None}
def ident(img,*a,**k):
    if state["ierr"]: raise state["ierr"]
    return state["ident"]
def diag(img,*a,**k):
    if state["derr"]: raise state["derr"]
    return state["diag"]
analysis_service.identify_plant=ident; analysis_service.diagnose_plant=diag
c=TestClient(app)
def img(fmt="PNG",exif=False):
    b=io.BytesIO(); im=Image.new("RGB",(640,480),"green")
    kw={}
    if exif:
        e=Image.Exif(); e[0x010F]="TelephoneTest"; e[0x8825]={1:"N",2:(48.0,35.0,0.0),3:"E",4:(6.0,10.0,0.0)}
        kw["exif"]=e
    im.save(b,fmt,**kw); return b.getvalue()
def show(n,r):
    try: body=r.json()
    except Exception: body=r.text
    print(f"[{n}] {r.status_code} {json.dumps(body,ensure_ascii=False)[:400]}")
P={"surname":"Dupont","name":"Jean","email":"jean@example.com","password":"motdepasse123"}
show("1 register",c.post("/auth/register",json=P))
show("2 register doublon",c.post("/auth/register",json=P))
show("3 register mdp court",c.post("/auth/register",json={**P,"email":"x@example.com","password":"abc"}))
show("4 login mauvais",c.post("/auth/login",json={"email":P["email"],"password":"faux"}))
show("4b login inconnu",c.post("/auth/login",json={"email":"nobody@example.com","password":"faux"}))
r=c.post("/auth/login",json={"email":P["email"],"password":P["password"]}); show("5 login ok",r)
H={"Authorization":"Bearer "+r.json()["access_token"]}
show("5b me",c.get("/auth/me",headers=H))
show("6 analyse sans jeton",c.post("/analysis",files={"image":("p.png",img(),"image/png")}))
r=c.post("/analysis",headers=H,files={"image":("p.jpg",img("JPEG",exif=True),"image/jpeg")},data={"plant_location":"Intérieur","plant_exposition":"Mi-ombre","plant_cultivation":"En pot"}); show("7 analyse ok",r)
aid=r.json()["id_analysis"] if "id_analysis" in r.json() else r.json().get("id")
show("8 faux png",c.post("/analysis",headers=H,files={"image":("p.png",b"ceci est du texte","image/png")}))
show("9 gif",c.post("/analysis",headers=H,files={"image":("p.gif",img("GIF"),"image/gif")}))
show("10 contexte invalide",c.post("/analysis",headers=H,files={"image":("p.png",img(),"image/png")},data={"plant_location":"Jardin secret"}))
state["ierr"]=PlantNotRecognizedError(); show("11 non plante",c.post("/analysis",headers=H,files={"image":("p.png",img(),"image/png")})); state["ierr"]=None
state["derr"]=DiagnosisUnavailableError(); show("12 moteur éteint",c.post("/analysis",headers=H,files={"image":("p.png",img(),"image/png")})); state["derr"]=None
big=b"\x89PNG"+b"0"*(storage.MAX_UPLOAD_BYTES+10); show("13 trop gros",c.post("/analysis",headers=H,files={"image":("p.png",big,"image/png")}))
show("14 historique",c.get("/history",headers=H))
files=[p for p in (tmp/"uploads").rglob("*") if p.is_file()]; print("fichiers sur disque:",[str(p.relative_to(tmp)) for p in files])
from sqlalchemy import select,func
from models.analysis import Analysis
with SF() as s: print("analyses en base:",s.scalar(select(func.count()).select_from(Analysis)))
stored=Image.open(files[0]); print("fichier stocké:",stored.format,stored.size,"exif:",dict(stored.getexif()))
r=c.get(f"/history/{aid}/image",headers=H); print("[15 image propriétaire]",r.status_code,r.headers["content-type"],r.headers.get("cache-control"))
c.post("/auth/register",json={**P,"email":"autre@example.com"}); r2=c.post("/auth/login",json={"email":"autre@example.com","password":P["password"]}); H2={"Authorization":"Bearer "+r2.json()["access_token"]}
show("16 autre: detail",c.get(f"/history/{aid}",headers=H2))
print("[16b autre: image]",c.get(f"/history/{aid}/image",headers=H2).status_code)
show("16c autre: historique",c.get("/history",headers=H2))
print("[16d autre: suppression]",c.delete(f"/history/{aid}",headers=H2).status_code)
r=c.delete(f"/history/{aid}",headers=H); print("[17 suppression proprio]",r.status_code)
show("17b detail apres",c.get(f"/history/{aid}",headers=H))
print("fichiers restants:",[p for p in (tmp/"uploads").rglob("*") if p.is_file()])
