'''
The code script outlines the task for internship application for Zorvyn.
Author - Himanshu Sandal
Date - 04 / 04 / 2026

Stack used = Fast API
Purpose - Internship Task

'''

# Installation of libraries
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from database import Base, engine , SessionLocal
import models
from schemas import TransactionCreate
from fastapi import HTTPException
from sqlalchemy import func


# Assigning role as a mandatory label in the API request header
def get_role(role: str = Query(...)):
    return role

app = FastAPI()
Base.metadata.create_all(bind=engine)
 
# To check if the API can estabilish connection or not
# A message "Finance API running" is thrown once the connection is estabilished successfully
@app.get("/")
def home():
    return {" message": "Finance API running"}


# DB CONNECTION
# Connect to local DB instance
# Stack - SQLlite
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST API

# This segment takes care of the creation of a transactions
# Loads the transaction to the DB

@app.post("/create_transactions")
def create_transaction(
    data :TransactionCreate,
    role : str = Depends(get_role),
    db: Session = Depends(get_db)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail= "Not allowed")
    txn = models.Transaction(**data.dict())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

# GET API

# The section allows the user to retrieve transaction details
# already loaded into the DB based on type and category only

@app.get("/get_transactions")
def get_transactions(
    type : str = None,
    category : str = None,
    db : Session = Depends(get_db)
):
    query = db.query(models.Transaction)

    if type:
        query = query.filter(models.Transaction.type == type)

    if category:
        query = query.filter(models.Transaction.category == category)

    return query.all()

# This section allows the user to update any transaction that may have been erroneous.
# it applied filters on the basis of id of the txn and then updates the data

@app.put("/update_transactions")
def update_transaction (
    id: int,
    data : TransactionCreate,
    role: str = Depends (get_role),
    db: Session = Depends (get_db)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail= "Transaction Not Found")
    txn = db.query(models.Transaction).filter(models.Transaction.id == id).first()

    if not txn:
        raise HTTPException(status_code=404, detail= "Transaction Not Found")
    
    #txn.id = data.id
    txn.amount = data.amount
    txn.type = data.type
    txn.category = data.category
    txn.date = data.date
    txn.description = data.description

    db.commit()
    db.refresh(txn)

    return txn

# This section deletes tranasactions based on the txn ID.

@app.delete("/delete_transactions")
def delete_transaction(
    id : int,
    role : str = Depends (get_role),
    db : Session = Depends (get_db)
):
    if role != "admin":
     raise HTTPException(status_code=403, detail= "Not  allowed")
    
    txn = db.query(models.Transaction).filter(models.Transaction.id == id).first()

    if not txn:
        raise HTTPException(status_code=404, detail= "Transaction Not Found")
     

    db.delete(txn)
    db.commit()

    return{"message": "Deleted successfully"}


# This section provides a comprehensive summary of the data that is being added into the 
# database. The following details are provided as a response
# 1. total income
# 2. total expense
# 3. balance i.e. income - expense
# The summary provied a view of the transaction that are available in the DB

@app.get("/get_summary")
def get_summary(db: Session = Depends(get_db)):
    
    income = db.query(func.sum(models.Transaction.amount))\
        .filter(models.Transaction.type == "income").scalar()

    expense = db.query(func.sum(models.Transaction.amount))\
        .filter(models.Transaction.type == "expense").scalar()

    # handle None values
    income = income or 0
    expense = expense or 0

    return {
        "total_income": income,
        "total_expense": expense,
        "balance": income - expense
    }         
    

# END

