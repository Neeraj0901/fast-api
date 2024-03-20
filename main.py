from fastapi import FastAPI, Form,Request, HTTPException
from typing import List,Optional
from pydantic import BaseModel,HttpUrl
from fastapi import File, UploadFile, Depends
from db import Base,SessionLocal,engine
import models
from typing import Annotated
from sqlalchemy.orm import Session
import os
from fastapi.staticfiles import StaticFiles
import secrets
from password_hash import Hash
from datetime import timedelta
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse

from fastapi_jwt_auth import AuthJWT
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = './media/user-profile/'


app = FastAPI()
app.mount('/media', StaticFiles(directory='media'),'media')


Base.metadata.create_all(bind=engine) #for migrations

def get_db():
   db = SessionLocal()
   try:
      yield db
   finally:
      db.close()
db_dependency = Annotated[Session, Depends(get_db)]
jwt =  Annotated[dict, Depends(AuthJWT)]


class Settings(BaseModel):
    authjwt_secret_key: str = "e76c2990b791c55fb874b867d4c803a2cc9c03cac58570cc6a62075b304ca8d0"
    authjwt_access_token_expires: int = timedelta(minutes=1)
    authjwt_refresh_token_expires: int = timedelta(days=30)
   
@AuthJWT.load_config
def get_config():
    return Settings()
 
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
   

class User(BaseModel):
   name:str
   email: str
   password: str

class Item1(BaseModel):
   name: str
   price: int
   user_id: int
   class Config:
        orm_mode = True

class UserList(BaseModel):
   id:int
   name:str
   email: str
   password: str
   profile: str | None = None
   item_data: list[Item1] | None = None
   class Config:
        orm_mode = True

class UserUpdate(BaseModel):
   name:Optional[str]
   email: Optional[str] = None
   
class Item(BaseModel):
   name: str
   price: int
   user_id: int
   user_data: UserList
   class Config:
        orm_mode = True


@app.get("/")
async def root():
   return {"message": "Hello World"}

@app.post("/createUser/", response_model=User)
async def root(user:User, db:db_dependency):
   user_obj = db.query(models.User).filter(models.User.email == user.email).first()
   if user_obj:
      return {'message': f"already present"}
   db_user = models.User(name=user.name, email=user.email,password=Hash.get_hash_password(user.password))
   db.add(db_user)
   db.commit()
   return db_user

@app.get("/listUser/", response_model=List[UserList])
async def root(db:db_dependency):
   user_obj = db.query(models.User).all()
   return user_obj

@app.post("/uploadProfile/{id}")
async def root(id,request : Request,db:db_dependency,fileield:UploadFile = File(...)):
   prefix_name = secrets.token_urlsafe(10)
   file_name = prefix_name+'--'+fileield.filename
   file_extension = file_name.split('.')[1]
   if file_extension not in ['png', 'jpg', 'jpeg']:
      return {'message':f"wrong formate {file_extension}"}
   file_path = UPLOAD_DIR+file_name
   file_content = await fileield.read()
   with open(file_path, 'wb') as file:
      file.write(file_content)
   user_obj = db.query(models.User).filter(models.User.id == id).first()
   user_obj.profile = file_path[1:]
   db.commit()
   aa = str(request.url).split('uploadProfile')[0]+user_obj.profile
   return {"message": aa}

@app.put("/updateUser/{id111}/")
async def root(id111,user:UserUpdate, db:db_dependency):
   user_obj = db.query(models.User).filter(models.User.id == id111).first()
   if not user_obj:
      return {'message': f"not present"}
   user_obj.name = user.name
   db.commit()
   return user_obj

@app.post("/createItem/", response_model=Item)
async def root(itemcr:Item, db:db_dependency):
   user_obj = db.query(models.User).filter(models.User.id == itemcr.user_id).first()
   
   if not user_obj:
      return {"message": "not a valid user"}
   db_item = models.Item(name=itemcr.name, price=itemcr.price,user_id=itemcr.user_id)
   db.add(db_item)
   db.commit()
   return db_item

@app.get("/listItem/", response_model=List[Item])
async def root(db:db_dependency):
   list_obj = db.query(models.Item).all()
   return list_obj



class User1(BaseModel):
    username: str
    password: str

@app.post('/login')
def login(user: User1,db:db_dependency, Authorize: jwt):
   user_obj = db.query(models.User).filter(models.User.name == user.username).first()
   if not user_obj:
      raise HTTPException(status_code=401,detail="User not present with this name")

   if not Hash.verify_password(user.password, user_obj.password):
      raise HTTPException(status_code=401,detail="Incorrect password")

   access_token = Authorize.create_access_token(subject=user.username)
   refresh_token = Authorize.create_refresh_token(subject=user.username)
   return {"access_token": access_token, "refresh_token": refresh_token}

@app.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}
  
@app.get('/user')
def user(Authorize: AuthJWT = Depends()):
   Authorize.jwt_required()

   current_user = Authorize.get_jwt_subject()
   return {"user": current_user}

# Product

# #work with file
# @app.post("/hello1/{name1}")
# async def root1(name1,id:int=Form(),name:str=Form(),fileield:UploadFile = File(...)):
#    import pdb;pdb.set_trace()
#    #file: UploadFile = File(...)
#    return {"message": f"Hello World {name1} --"}

