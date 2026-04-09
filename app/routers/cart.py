from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import DB
from app.models.orm import DesignGeneration, GenerationProduct, Product, Project
from app.models.schemas import CartItem, CartResponse, TrackClickResponse
from app.services.auth import CurrentUser

router = APIRouter(tags=["Cart"])


class TrackClickRequest(BaseModel):
    project_id: UUID
    product_id: UUID
    user_id: UUID


@router.get("/projects/{id}/cart", response_model=CartResponse)
async def get_cart(id: UUID, db: DB, current_user: CurrentUser):
    project = db.query(Project).filter(
        Project.project_id == id,
        Project.user_id == current_user,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    seen: set = set()
    items: list[CartItem] = []
    total = 0.0

    for gen in db.query(DesignGeneration).filter(DesignGeneration.project_id == id).all():
        for gp in gen.generation_products:
            if gp.product_id in seen:
                continue
            seen.add(gp.product_id)
            product = db.query(Product).filter(Product.product_id == gp.product_id).first()
            if product:
                price = float(product.price or 0)
                total += price
                items.append(CartItem(
                    product_id=product.product_id,
                    name=product.name or "",
                    price=price,
                    affiliate_url=product.product_url,
                ))

    return CartResponse(total=round(total, 2), items=items)


@router.post("/cart/track", response_model=TrackClickResponse)
async def track_affiliate_click(body: TrackClickRequest, db: DB, current_user: CurrentUser):
    product = db.query(Product).filter(Product.product_id == body.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    redirect_url = product.product_url or "https://www.ikea.com/sg/en/"
    return TrackClickResponse(tracked=True, redirect_url=redirect_url)
