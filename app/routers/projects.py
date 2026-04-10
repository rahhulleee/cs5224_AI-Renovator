import uuid
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import DB
from app.models.orm import DesignGeneration, GenerationProduct, Photo, Product, Project
from app.models.schemas import BudgetLineItem, BudgetState
from app.models.schemas import Project as ProjectSchema
from app.services.auth import CurrentUser
from app.services.s3 import presign_upload

router = APIRouter(prefix="/projects", tags=["Projects"])


# ── Request bodies ────────────────────────────────────────────────────────────

class CreateProjectRequest(BaseModel):
    title: str
    room_type: str | None = None
    style_prompt: str | None = None
    budget_limit: float | None = None


class UpdateBudgetRequest(BaseModel):
    budget_limit: float


class PresignRequest(BaseModel):
    file_name: str
    content_type: str = "image/jpeg"


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("", response_model=ProjectSchema, status_code=201)
async def create_project(body: CreateProjectRequest, db: DB, current_user: CurrentUser):
    project = Project(
        user_id=current_user,
        title=body.title,
        room_type=body.room_type,
        style_prompt=body.style_prompt,
        budget_limit=body.budget_limit,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _to_schema(project)


@router.get("", response_model=list[ProjectSchema])
async def list_projects(db: DB, current_user: CurrentUser):
    projects = db.query(Project).filter(Project.user_id == current_user).all()
    return [_to_schema(p) for p in projects]


@router.get("/{id}", response_model=ProjectSchema)
async def get_project(id: UUID, db: DB, current_user: CurrentUser):
    return _to_schema(_get_owned(id, current_user, db))


@router.delete("/{id}", status_code=204)
async def delete_project(id: UUID, db: DB, current_user: CurrentUser):
    project = _get_owned(id, current_user, db)
    db.delete(project)
    db.commit()


@router.post("/{id}/uploads/presign")
async def presign_upload_url(id: UUID, body: PresignRequest, db: DB, current_user: CurrentUser):
    project = _get_owned(id, current_user, db)
    s3_key = f"uploads/{project.project_id}/{uuid.uuid4()}/{body.file_name}"
    photo = Photo(
        project_id=project.project_id,
        photo_type="original",
        s3_key=s3_key,
        file_name=body.file_name,
        mime_type=body.content_type,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    upload_url = presign_upload(s3_key, body.content_type)
    return {
        "photo_id": photo.photo_id,
        "upload_url": upload_url,
        "s3_key": s3_key,
        "expires_in": 3600,
    }


@router.get("/{id}/budget", response_model=BudgetState)
async def get_budget(id: UUID, db: DB, current_user: CurrentUser):
    project = _get_owned(id, current_user, db)
    return _build_budget(project, db)


@router.put("/{id}/budget", response_model=BudgetState)
async def update_budget(id: UUID, body: UpdateBudgetRequest, db: DB, current_user: CurrentUser):
    project = _get_owned(id, current_user, db)
    project.budget_limit = body.budget_limit
    db.commit()
    db.refresh(project)
    return _build_budget(project, db)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_owned(project_id: UUID, user_id: UUID, db) -> Project:
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == user_id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _to_schema(project: Project) -> ProjectSchema:
    return ProjectSchema(
        project_id=project.project_id,
        name=project.title or "",
        budget_limit=float(project.budget_limit) if project.budget_limit is not None else None,
        created_at=project.created_at or datetime.utcnow(),
        photo_ids=[p.photo_id for p in project.photos],
        generation_ids=[g.design_id for g in project.generations],
    )


def _build_budget(project: Project, db) -> BudgetState:
    items: list[BudgetLineItem] = []
    seen: set = set()
    for gen in project.generations:
        for gp in gen.generation_products:
            if gp.product_id in seen:
                continue
            seen.add(gp.product_id)
            product = db.query(Product).filter(Product.product_id == gp.product_id).first()
            if product:
                items.append(BudgetLineItem(
                    product_id=product.product_id,
                    name=product.name or "",
                    price=float(product.price or 0),
                    source=product.external_source or "scraped",
                ))
    spent = sum(i.price for i in items)
    limit = float(project.budget_limit) if project.budget_limit is not None else 0.0
    return BudgetState(
        limit=limit,
        spent=spent,
        remaining=max(0.0, limit - spent),
        over_budget=spent > limit if limit > 0 else False,
        items=items,
    )
