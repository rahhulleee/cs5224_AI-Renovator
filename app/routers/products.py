from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.schemas import Product, ProductDetail, ScrapedProduct, Substitute
from app.services.provider_registry import Providers, get_providers

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[Product])
async def search_products(
    providers: Providers,
    q: str | None = Query(None, description="Free-text search"),
    style: str | None = Query(None, examples=["scandinavian"]),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    source: Literal["ikea", "taobao"] | None = Query(None),
    in_stock: bool | None = Query(None),
):
    if not providers:
        raise HTTPException(status_code=400, detail=f"Unknown source: {source!r}")

    results: list[Product] = []
    for provider in providers:
        results.extend(
            await provider.search(
                q=q,
                style=style,
                min_price=min_price,
                max_price=max_price,
                in_stock=in_stock,
            )
        )
    return results


@router.get("/{id}", response_model=ProductDetail)
async def get_product(
    id: UUID,
    providers: Providers,
):
    for provider in providers:
        detail = await provider.get_product(str(id))
        if detail is not None:
            return detail
    raise HTTPException(status_code=404, detail="Product not found")



@router.get("/{id}/substitutes", response_model=list[Substitute])
async def get_substitutes(
    id: UUID,
    max_price: float = Query(..., ge=0),
    reason: Literal["over_budget", "out_of_stock"] = Query(...),
):
    # TODO: find visually similar products within budget
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/from-url", response_model=ScrapedProduct)
async def index_product_from_url(body: dict):
    # TODO: scrape and normalise product from arbitrary URL
    # body: { url: str }
    raise HTTPException(status_code=501, detail="Not implemented")
