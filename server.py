from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
import os
import shutil
from sqlalchemy.orm import Session
import uvicorn
from database import SessionLocal, engine
from models import Base, User
from schemas import UserRegister, UserUpdate, UserLogin
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/API/Login"
)

Base.metadata.create_all(bind=engine)


# -------------------------
# Database Connection
# -------------------------
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# -------------------------
# Home API
# -------------------------
@app.get("/")
def home():

    return {
        "message": "EndpointAPI Server Running"
    }


# -------------------------
# Register API
# -------------------------
@app.post("/API/RegisterEndpoint")
def register(user: UserRegister, db: Session = Depends(get_db)):

    try:

        existing_user = db.query(User).filter(
            User.username == user.username
        ).first()

        if existing_user:
            return {
                "message": "Username already exists"
            }

        hashed = hash_password(user.password)

        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User Registered Successfully",
            "id": new_user.id
        }

    except Exception as e:
        return {
            "error": str(e)
        }#get endpoint
@app.get("/API/GetEndpointInfo")
def get_endpoint_info():

    return {

        "Application": "EndpointAPI",

        "Version": "1.0",

        "Framework": "FastAPI",

        "Database": "SQLite",

        "Status": "Running",

        "AvailableEndpoints": [

            "/API/RegisterEndpoint",

            "/API/GetEndpointInfo",

            "/API/UploadData"

        ]
    }

#Get All Users
@app.get("/API/GetAllUsers")
def get_all_users(db: Session = Depends(get_db)):

    users = db.query(User).all()

    return users
@app.get("/API/GetUser/{id}")   # Get All User using id
def get_user(id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == id).first()

    if user is None:
        return {
            "message": "User Not Found"
        }

    return user
# update user
@app.put("/API/UpdateUser/{id}")
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.id == id).first()

    if db_user is None:
        return {
            "message": "User Not Found"
        }

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = hash_password(user.password)

    db.commit()
    db.refresh(db_user)

    return {
        "message": "User Updated Successfully",
        "user": db_user
    }
#Delete User
@app.delete("/API/DeleteUser/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.id == id).first()

    if db_user is None:
        return {
            "message": "User Not Found"
        }

    db.delete(db_user)

    db.commit()

    return {
        "message": "User Deleted Successfully"
    }
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/API/UploadData")
async def upload_data(file: UploadFile = File(...)):

    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Upload Successful",
        "filename": file.filename
    }

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
