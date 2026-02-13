from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DatasetVersionBase(BaseModel):
    version_number: int
    file_size: int

class DatasetVersion(DatasetVersionBase):
    id: int
    dataset_id: int
    download_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DatasetBase(BaseModel):
    name: str
    description: str
    is_public: bool = False

class DatasetCreate(DatasetBase):
    pass

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class Dataset(DatasetBase):
    id: int
    owner_id: int
    downloads: int
    created_at: datetime
    updated_at: datetime
    owner: User
    versions: List[DatasetVersion] = []
    
    class Config:
        from_attributes = True
