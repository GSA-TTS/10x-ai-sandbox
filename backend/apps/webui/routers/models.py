import logging
import sys

from fastapi import Depends, FastAPI, HTTPException, status, Request
from datetime import datetime, timedelta
from typing import List, Union, Optional

from fastapi import APIRouter
from pydantic import BaseModel
import json
from apps.webui.models.models import Models, ModelModel, ModelForm, ModelResponse

from utils.utils import get_verified_user  # , get_admin_user
from constants import ERROR_MESSAGES

logging.basicConfig(stream=sys.stdout, level="INFO")
log = logging.getLogger(__name__)

router = APIRouter()

###########################
# getModels
###########################


@router.get("/", response_model=List[ModelResponse])
async def get_models(user=Depends(get_verified_user)):
    return Models.get_all_models()


############################
# AddNewModel
############################


@router.post("/add", response_model=Optional[ModelModel])
async def add_new_model(
    request: Request, form_data: ModelForm, user=Depends(get_verified_user)
):
    hyphenated_user_name = user.name.replace(" ", "-").lower()
    if hyphenated_user_name not in form_data.id and user.role == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be an admin to create an unattributed model",
        )
    if form_data.id in request.app.state.MODELS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.MODEL_ID_TAKEN,
        )
    else:
        model = Models.insert_new_model(form_data, user.id)

        if model:
            return model
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.DEFAULT(),
            )


############################
# GetModelById
############################


@router.get("/", response_model=Optional[ModelModel])
async def get_model_by_id(id: str, user=Depends(get_verified_user)):
    model = Models.get_model_by_id(id)

    if model:
        return model
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdateModelById
############################


@router.post("/update", response_model=Optional[ModelModel])
async def update_model_by_id(
    request: Request, id: str, form_data: ModelForm, user=Depends(get_verified_user)
):
    hyphenated_user_name = user.name.replace(" ", "-").lower()

    log.error(
        f"hyphenated_user_name: {hyphenated_user_name}\nid: {id}\nform_data: {form_data}"
    )

    if hyphenated_user_name not in id and user.role == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be an admin to update this model",
        )
    model = Models.get_model_by_id(id)
    if model:
        model = Models.update_model_by_id(id, form_data)
        return model
    else:
        log.error("Couldn't find model in database")
        if form_data.id in request.app.state.MODELS:
            model = Models.insert_new_model(form_data, user.id)
            if model:
                return model
            else:
                log.error("Error inserting new model")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ERROR_MESSAGES.DEFAULT(),
                )
        else:
            log.error("Couldn't find model in app state")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.DEFAULT(),
            )


############################
# DeleteModelById
############################


@router.delete("/delete", response_model=bool)
async def delete_model_by_id(id: str, user=Depends(get_verified_user)):
    hyphenated_user_name = user.name.replace(" ", "-").lower()
    log.error(f"hyphenated_user_name: {hyphenated_user_name}\nid: {id}")
    if hyphenated_user_name not in id and user.role == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be an admin to delete this model",
        )
    result = Models.delete_model_by_id(id)
    return result
