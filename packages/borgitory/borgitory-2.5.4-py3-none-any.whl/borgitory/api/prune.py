"""
API endpoints for managing prune configurations (archive pruning policies)
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse

from borgitory.models.schemas import (
    PruneConfigCreate,
    PruneConfigUpdate,
)

from borgitory.dependencies import (
    TemplatesDep,
    PruneServiceDep,
    get_browser_timezone_offset,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/form", response_class=HTMLResponse)
async def get_prune_form(
    request: Request,
    templates: TemplatesDep,
    service: PruneServiceDep,
) -> HTMLResponse:
    """Get manual prune form with repositories populated"""
    form_data = service.get_form_data()

    return templates.TemplateResponse(
        request,
        "partials/prune/config_form.html",
        form_data,
    )


@router.get("/policy-form", response_class=HTMLResponse)
async def get_policy_form(
    request: Request,
    templates: TemplatesDep,
) -> HTMLResponse:
    """Get policy creation form"""
    return templates.TemplateResponse(
        request,
        "partials/prune/create_form.html",
        {},
    )


@router.get("/strategy-fields", response_class=HTMLResponse)
async def get_strategy_fields(
    request: Request, templates: TemplatesDep, strategy: str = "simple"
) -> HTMLResponse:
    """Get dynamic strategy fields based on selection"""
    return templates.TemplateResponse(
        request,
        "partials/prune/strategy_fields.html",
        {"strategy": strategy},
    )


@router.post("/", response_class=HTMLResponse)
async def create_prune_config(
    request: Request,
    prune_config: PruneConfigCreate,
    templates: TemplatesDep,
    service: PruneServiceDep,
) -> HTMLResponse:
    """Create a new prune configuration"""
    result = service.create_prune_config(prune_config)

    if result.success and result.config:
        response = templates.TemplateResponse(
            request,
            "partials/prune/create_success.html",
            {"config_name": result.config.name},
        )
        response.headers["HX-Trigger"] = "pruneConfigUpdate"
        return response
    else:
        return templates.TemplateResponse(
            request,
            "partials/prune/create_error.html",
            {"error_message": result.error_message},
            status_code=400,
        )


@router.get("/", response_class=HTMLResponse)
def get_prune_configs(
    request: Request,
    templates: TemplatesDep,
    service: PruneServiceDep,
) -> str:
    """Get prune configurations as formatted HTML"""
    try:
        processed_configs = service.get_configs_with_descriptions()

        browser_tz_offset = get_browser_timezone_offset(request)
        return templates.get_template("partials/prune/config_list_content.html").render(
            request=request,
            configs=processed_configs,
            browser_tz_offset=browser_tz_offset,
        )

    except Exception as e:
        return templates.get_template("partials/jobs/error_state.html").render(
            message=f"Error loading prune configurations: {str(e)}", padding="4"
        )


@router.post("/{config_id}/enable", response_class=HTMLResponse)
async def enable_prune_config(
    request: Request,
    config_id: int,
    templates: TemplatesDep,
    service: PruneServiceDep,
) -> _TemplateResponse:
    """Enable a prune configuration"""
    result = service.enable_prune_config(config_id)

    if result.success and result.config:
        response = templates.TemplateResponse(
            request,
            "partials/prune/action_success.html",
            {"message": f"Prune policy '{result.config.name}' enabled successfully!"},
        )
        response.headers["HX-Trigger"] = "pruneConfigUpdate"
        return response
    else:
        return templates.TemplateResponse(
            request,
            "partials/prune/action_error.html",
            {"error_message": result.error_message},
            status_code=404,
        )


@router.post("/{config_id}/disable", response_class=HTMLResponse)
async def disable_prune_config(
    request: Request,
    config_id: int,
    templates: TemplatesDep,
    service: PruneServiceDep,
) -> HTMLResponse:
    """Disable a prune configuration"""
    result = service.disable_prune_config(config_id)

    if result.success and result.config:
        response = templates.TemplateResponse(
            request,
            "partials/prune/action_success.html",
            {"message": f"Prune policy '{result.config.name}' disabled successfully!"},
        )
        response.headers["HX-Trigger"] = "pruneConfigUpdate"
        return response
    else:
        return templates.TemplateResponse(
            request,
            "partials/prune/action_error.html",
            {"error_message": result.error_message},
            status_code=404,
        )


@router.get("/{config_id}/edit", response_class=HTMLResponse)
async def get_prune_config_edit_form(
    request: Request,
    config_id: int,
    templates: TemplatesDep,
    service: PruneServiceDep,
) -> HTMLResponse:
    """Get edit form for a specific prune configuration"""
    config = service.get_prune_config_by_id(config_id)

    if not config:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Prune configuration not found")

    context = {
        "config": config,
        "is_edit_mode": True,
    }

    return templates.TemplateResponse(request, "partials/prune/edit_form.html", context)


@router.put("/{config_id}", response_class=HTMLResponse)
async def update_prune_config(
    request: Request,
    config_id: int,
    config_update: PruneConfigUpdate,
    templates: TemplatesDep,
    service: PruneServiceDep,
) -> HTMLResponse:
    """Update a prune configuration"""
    result = service.update_prune_config(config_id, config_update)

    if result.success and result.config:
        response = templates.TemplateResponse(
            request,
            "partials/prune/update_success.html",
            {"config_name": result.config.name},
        )
        response.headers["HX-Trigger"] = "pruneConfigUpdate"
        return response
    else:
        return templates.TemplateResponse(
            request,
            "partials/prune/update_error.html",
            {"error_message": result.error_message},
            status_code=404,
        )


@router.delete("/{config_id}", response_class=HTMLResponse)
async def delete_prune_config(
    request: Request,
    config_id: int,
    templates: TemplatesDep,
    service: PruneServiceDep,
) -> HTMLResponse:
    """Delete a prune configuration"""
    result = service.delete_prune_config(config_id)

    if result.success:
        response = templates.TemplateResponse(
            request,
            "partials/prune/action_success.html",
            {
                "message": f"Prune configuration '{result.config_name}' deleted successfully!"
            },
        )
        response.headers["HX-Trigger"] = "pruneConfigUpdate"
        return response
    else:
        return templates.TemplateResponse(
            request,
            "partials/prune/action_error.html",
            {"error_message": result.error_message},
            status_code=404,
        )
