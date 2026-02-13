from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.models import Dataset, DatasetVersion, User
from app.schemas.schemas import Dataset as DatasetSchema, DatasetCreate, DatasetUpdate
import os
import shutil

router = APIRouter(prefix="/datasets", tags=["datasets"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=DatasetSchema)
def create_dataset(dataset: DatasetCreate, owner_id: int, db: Session = Depends(get_db)):
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_dataset = Dataset(
        name=dataset.name,
        description=dataset.description,
        owner_id=owner_id,
        is_public=dataset.is_public
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

@router.get("/", response_model=list[DatasetSchema])
def list_datasets(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    datasets = db.query(Dataset).filter(Dataset.is_public == True).offset(skip).limit(limit).all()
    return datasets

@router.get("/{dataset_id}", response_model=DatasetSchema)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.put("/{dataset_id}", response_model=DatasetSchema)
def update_dataset(dataset_id: int, dataset: DatasetUpdate, owner_id: int, db: Session = Depends(get_db)):
    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if db_dataset.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if dataset.name:
        db_dataset.name = dataset.name
    if dataset.description:
        db_dataset.description = dataset.description
    if dataset.is_public is not None:
        db_dataset.is_public = dataset.is_public
    
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, owner_id: int, db: Session = Depends(get_db)):
    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if db_dataset.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(db_dataset)
    db.commit()
    return {"message": "Dataset deleted"}

@router.post("/{dataset_id}/upload")
async def upload_dataset_file(dataset_id: int, file: UploadFile = File(...), owner_id: int = None, db: Session = Depends(get_db)):
    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if db_dataset.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    version_number = len(db_dataset.versions) + 1
    file_size = os.path.getsize(file_path)
    
    version = DatasetVersion(
        dataset_id=dataset_id,
        version_number=version_number,
        file_path=file_path,
        file_size=file_size
    )
    db.add(version)
    db.commit()
    
    return {"message": "File uploaded successfully", "version": version_number}
