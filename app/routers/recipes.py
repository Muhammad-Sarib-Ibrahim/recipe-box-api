from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Recipe, User
from app.schemas import RecipeCreate, RecipeRead, RecipeUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("", response_model=List[RecipeRead])
def list_recipes(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    recipes = session.exec(
        select(Recipe).where(Recipe.owner_id == current_user.id)
    ).all()
    return recipes


@router.post("", response_model=RecipeRead)
def create_recipe(
    recipe_in: RecipeCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    recipe = Recipe(**recipe_in.model_dump(), owner_id=current_user.id)
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


def _get_owned_recipe(recipe_id: int, session: Session, current_user: User) -> Recipe:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.owner_id != current_user.id:
        # Note: 404, not 403 — we don't want to reveal that a recipe
        # with this ID exists but belongs to someone else.
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(
    recipe_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_recipe(recipe_id, session, current_user)


@router.put("/{recipe_id}", response_model=RecipeRead)
def update_recipe(
    recipe_id: int,
    recipe_in: RecipeUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    recipe = _get_owned_recipe(recipe_id, session, current_user)
    update_data = recipe_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(recipe, key, value)
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(
    recipe_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    recipe = _get_owned_recipe(recipe_id, session, current_user)
    session.delete(recipe)
    session.commit()
