import logging
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Form,
    File,
    UploadFile,
    Request,
)
from fastapi.responses import HTMLResponse, StreamingResponse, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from borgitory.models.database import Repository, User, get_db
from borgitory.models.schemas import (
    Repository as RepositorySchema,
    RepositoryCreate,
    RepositoryUpdate,
)
from borgitory.dependencies import (
    BorgServiceDep,
    ArchiveManagerDep,
    TemplatesDep,
    RepositoryServiceDep,
    PathServiceDep,
)
from borgitory.models.repository_dtos import (
    CreateRepositoryRequest,
    ImportRepositoryRequest,
    DeleteRepositoryRequest,
)
from borgitory.utils.datetime_utils import (
    format_datetime_for_display,
    parse_datetime_string,
)
from borgitory.utils.template_responses import (
    RepositoryResponseHandler,
    ArchiveResponseHandler,
)
from borgitory.api.auth import get_current_user
from borgitory.utils.secure_path import (
    DirectoryInfo,
    secure_exists,
    secure_isdir,
    get_directory_listing,
)
from borgitory.utils.path_prefix import (
    parse_path_for_autocomplete,
)
from starlette.templating import _TemplateResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class DirectoryListResponse(BaseModel):
    """Response model for directory listing"""

    directories: List[DirectoryInfo]

    class Config:
        from_attributes = True


@router.post("/")
async def create_repository(
    request: Request,
    repo: RepositoryCreate,
    repo_svc: RepositoryServiceDep,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """Create a new repository - thin controller using business logic service."""
    # Convert to DTO
    create_request = CreateRepositoryRequest(
        name=repo.name,
        path=repo.path,
        passphrase=repo.passphrase or "",
        user_id=current_user.id,
        cache_dir=repo.cache_dir,
    )

    # Call business service
    result = await repo_svc.create_repository(create_request, db)

    # Handle response formatting
    return RepositoryResponseHandler.handle_create_response(request, result)


@router.get("/", response_model=List[RepositorySchema])
def list_repositories(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[Repository]:
    repositories = db.query(Repository).offset(skip).limit(limit).all()
    return repositories


@router.get("/html", response_class=HTMLResponse)
def get_repositories_html(
    request: Request,
    templates: TemplatesDep,
    db: Session = Depends(get_db),
) -> _TemplateResponse:
    """Get repositories as HTML for frontend display"""
    try:
        repositories = db.query(Repository).all()
        return templates.TemplateResponse(
            request,
            "partials/repositories/list_content.html",
            {"repositories": repositories},
        )
    except Exception as e:
        return templates.TemplateResponse(
            request,
            "partials/common/error_message.html",
            {
                "error_message": f"Error loading repositories: {str(e)}",
            },
        )


@router.get("/directories", response_model=DirectoryListResponse)
async def list_directories(path: str = "/") -> DirectoryListResponse:
    """List directories at the given path for autocomplete functionality."""

    try:
        if not secure_exists(path):
            return DirectoryListResponse(directories=[])

        if not secure_isdir(path):
            return DirectoryListResponse(directories=[])

        directories = get_directory_listing(path, include_files=False)

        return DirectoryListResponse(directories=directories)

    except Exception as e:
        logger.error(f"Error listing directories at {path}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list directories: {str(e)}"
        )


@router.get("/directories/autocomplete", response_class=HTMLResponse)
async def list_directories_autocomplete(
    request: Request,
    templates: TemplatesDep,
    repo_svc: RepositoryServiceDep,
    path_service: PathServiceDep,
    current_user: User = Depends(get_current_user),
) -> _TemplateResponse:
    """List directories as HTML for autocomplete functionality."""

    # Get the input value from the form data
    form_data = (
        await request.form() if request.method == "POST" else request.query_params
    )
    input_value = ""

    # Try to get the input value from various possible parameter names
    for param_name in form_data.keys():
        if param_name in [
            "path",
            "source_path",
            "create-path",
            "import-path",
            "backup-source-path",
            "schedule-source-path",
            "cache_dir",
            "create-cache-dir",
            "import-cache-dir",
        ]:
            input_value = str(form_data.get(param_name, ""))
            break

    if not input_value:
        # Always use Unix root for WSL-first approach
        input_value = "/"

    # Parse the normalized path to get directory and search term
    dir_path, search_term = parse_path_for_autocomplete(input_value, path_service)

    try:
        # Use repository service to handle directory listing across platforms
        directories = await repo_svc.list_directories_for_autocomplete(
            dir_path, search_term, include_files=False
        )

        # Get the target input ID from headers
        target_input = request.headers.get("hx-target-input", "")

        return templates.TemplateResponse(
            request,
            "partials/shared/path_autocomplete_dropdown.html",
            {
                "directories": directories,
                "search_term": search_term,
                "target_input": target_input,
                "input_value": input_value,
            },
        )

    except Exception as e:
        logger.error(f"Error listing directories at {dir_path}: {e}")
        return templates.TemplateResponse(
            request,
            "partials/shared/path_autocomplete_dropdown.html",
            {
                "directories": [],
                "search_term": search_term,
                "target_input": "",
                "error": str(e),
            },
        )


@router.get("/import-form", response_class=HTMLResponse)
async def get_import_form(
    request: Request, templates: TemplatesDep
) -> _TemplateResponse:
    """Get the import repository form"""
    return templates.TemplateResponse(
        request, "partials/repositories/import/form_import.html"
    )


@router.get("/import-encryption-fields", response_class=HTMLResponse)
async def get_import_encryption_fields(
    request: Request,
    templates: TemplatesDep,
    encryption_type: str = "",
) -> _TemplateResponse:
    """Get the appropriate encryption fields based on encryption type selection."""
    return templates.TemplateResponse(
        request,
        "partials/repositories/import/encryption_fields.html",
        {"encryption_type": encryption_type},
    )


@router.get("/create-form", response_class=HTMLResponse)
async def get_create_form(
    request: Request, templates: TemplatesDep
) -> _TemplateResponse:
    """Get the create repository form"""
    return templates.TemplateResponse(
        request, "partials/repositories/create/form_create.html"
    )


@router.post("/import")
async def import_repository(
    request: Request,
    repo_svc: RepositoryServiceDep,
    name: str = Form(...),
    path: str = Form(...),
    passphrase: str = Form(...),
    keyfile: UploadFile = File(None),
    encryption_type: str = Form(None),
    keyfile_content: str = Form(None),
    cache_dir: str = Form(None),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Import an existing Borg repository - thin controller using business logic service."""
    import_request = ImportRepositoryRequest(
        name=name,
        path=path.strip(),
        passphrase=passphrase,
        keyfile=keyfile,
        encryption_type=encryption_type,
        keyfile_content=keyfile_content,
        user_id=None,  # Import doesn't require user ID currently
        cache_dir=cache_dir.strip(),
    )

    result = await repo_svc.import_repository(import_request, db)

    return RepositoryResponseHandler.handle_import_response(request, result)


@router.get("/{repo_id}", response_model=RepositorySchema)
def get_repository(repo_id: int, db: Session = Depends(get_db)) -> Repository:
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repository


@router.put("/{repo_id}", response_model=RepositorySchema)
def update_repository(
    repo_id: int, repo_update: RepositoryUpdate, db: Session = Depends(get_db)
) -> Repository:
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    update_data = repo_update.model_dump(exclude_unset=True)

    if "passphrase" in update_data:
        repository.set_passphrase(update_data.pop("passphrase"))

    for field, value in update_data.items():
        setattr(repository, field, value)

    db.commit()
    db.refresh(repository)
    return repository


@router.get("/{repo_id}/lock-status", response_class=HTMLResponse)
async def check_repository_lock_status(
    repo_id: int,
    request: Request,
    repo_svc: RepositoryServiceDep,
    templates: TemplatesDep,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Check if a repository is currently locked."""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    lock_status = await repo_svc.check_repository_lock_status(repository)

    return templates.TemplateResponse(
        request,
        "partials/repositories/modal/lock_status.html",
        {
            "repo_id": repo_id,
            "locked": lock_status.get("locked", False),
            "accessible": lock_status.get("accessible", False),
            "message": lock_status.get("message", "Unknown status"),
        },
    )


@router.get("/{repo_id}/details-modal", response_class=HTMLResponse)
async def get_repository_details_modal(
    repo_id: int,
    request: Request,
    templates: TemplatesDep,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Get the repository details modal."""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    return templates.TemplateResponse(
        request,
        "partials/repositories/modal/details_modal.html",
        {
            "repository": repository,
        },
    )


@router.get("/modal/close", response_class=HTMLResponse)
async def close_repository_modal() -> HTMLResponse:
    """Close the repository details modal."""
    return HTMLResponse(content="")


@router.get("/{repo_id}/break-lock-button", response_class=HTMLResponse)
async def get_break_lock_button(
    repo_id: int,
    request: Request,
    repo_svc: RepositoryServiceDep,
    templates: TemplatesDep,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Get the break lock button if repository is locked."""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    lock_status = await repo_svc.check_repository_lock_status(repository)

    return templates.TemplateResponse(
        request,
        "partials/repositories/modal/break_lock_button.html",
        {
            "repo_id": repo_id,
            "repo_name": repository.name,
            "show_break_lock_button": lock_status.get("locked", False),
        },
    )


@router.get("/{repo_id}/break-lock-button-modal", response_class=HTMLResponse)
async def get_break_lock_button_modal(
    repo_id: int,
    request: Request,
    repo_svc: RepositoryServiceDep,
    templates: TemplatesDep,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Get the break lock button for modal if repository is locked."""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    lock_status = await repo_svc.check_repository_lock_status(repository)

    return templates.TemplateResponse(
        request,
        "partials/repositories/modal/break_lock_button_modal.html",
        {
            "repo_id": repo_id,
            "repo_name": repository.name,
            "show_break_lock_button": lock_status.get("locked", False),
        },
    )


@router.post("/{repo_id}/break-lock", response_class=HTMLResponse)
async def break_repository_lock(
    repo_id: int,
    request: Request,
    repo_svc: RepositoryServiceDep,
    templates: TemplatesDep,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Break a repository lock and return updated repository list."""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    await repo_svc.break_repository_lock(repository)

    # Return the updated repository list
    repositories = db.query(Repository).all()
    return templates.TemplateResponse(
        request,
        "partials/repositories/list_content.html",
        {
            "repositories": repositories,
        },
    )


@router.post("/{repo_id}/break-lock-modal", response_class=HTMLResponse)
async def break_repository_lock_modal(
    repo_id: int,
    request: Request,
    repo_svc: RepositoryServiceDep,
    templates: TemplatesDep,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Break a repository lock from modal and return updated lock status."""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    await repo_svc.break_repository_lock(repository)

    # Return updated lock status for the modal
    lock_status = await repo_svc.check_repository_lock_status(repository)

    return templates.TemplateResponse(
        request,
        "partials/repositories/modal/lock_status.html",
        {
            "repo_id": repo_id,
            "locked": lock_status.get("locked", False),
            "accessible": lock_status.get("accessible", False),
            "message": lock_status.get("message", "Unknown status"),
        },
    )


@router.get("/{repo_id}/borg-info", response_class=HTMLResponse)
async def get_repository_borg_info(
    repo_id: int,
    request: Request,
    repo_svc: RepositoryServiceDep,
    templates: TemplatesDep,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Get detailed repository information from borg info command."""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    info_result = await repo_svc.get_repository_info(repository)

    return templates.TemplateResponse(
        request,
        "partials/repositories/modal/borg_info.html",
        info_result,
    )


@router.get("/{repo_id}/export-key")
async def export_repository_key(
    repo_id: int,
    repo_svc: RepositoryServiceDep,
    db: Session = Depends(get_db),
) -> Response:
    """Export repository key as a downloadable file."""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    result = await repo_svc.export_repository_key(repository)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error_message"])

    # Return the key as a downloadable text file
    return Response(
        content=result["key_data"],
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{result["filename"]}"'},
    )


@router.delete("/{repo_id}", response_class=HTMLResponse)
async def delete_repository(
    repo_id: int,
    request: Request,
    repo_svc: RepositoryServiceDep,
    delete_borg_repo: bool = False,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Delete a repository - thin controller using business logic service."""
    delete_request = DeleteRepositoryRequest(
        repository_id=repo_id,
        delete_borg_repo=delete_borg_repo,
        user_id=None,  # Delete doesn't require user ID currently
    )

    result = await repo_svc.delete_repository(delete_request, db)

    return RepositoryResponseHandler.handle_delete_response(request, result)


@router.get("/{repo_id}/archives")
async def list_archives(
    request: Request,
    repo_id: int,
    repo_svc: RepositoryServiceDep,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """List repository archives - thin controller using business logic service."""
    result = await repo_svc.list_archives(repo_id, db)

    return ArchiveResponseHandler.handle_archive_listing_response(request, result)


@router.get("/archives/selector")
async def get_archives_repository_selector(
    request: Request,
    templates: TemplatesDep,
    db: Session = Depends(get_db),
    preselect_repo: str = "",
) -> _TemplateResponse:
    """Get repository selector for archives with repositories populated"""
    repositories = db.query(Repository).all()

    return templates.TemplateResponse(
        request,
        "partials/archives/repository_selector.html",
        {"repositories": repositories, "preselect_repo": preselect_repo},
    )


@router.get("/archives/loading")
async def get_archives_loading(
    request: Request, templates: TemplatesDep
) -> _TemplateResponse:
    """Get loading state for archives"""
    return templates.TemplateResponse(
        request, "partials/archives/loading_state.html", {}
    )


@router.post("/archives/load-with-spinner")
async def load_archives_with_spinner(
    request: Request, templates: TemplatesDep, repository_id: str = Form("")
) -> _TemplateResponse:
    """Show loading spinner then trigger loading actual archives"""
    if not repository_id or repository_id == "":
        return templates.TemplateResponse(
            request, "partials/archives/empty_state.html", {}
        )

    try:
        repo_id = int(repository_id)
        return templates.TemplateResponse(
            request,
            "partials/archives/loading_with_trigger.html",
            {"repository_id": repo_id},
        )
    except (ValueError, TypeError):
        return templates.TemplateResponse(
            request, "partials/archives/empty_state.html", {}
        )


@router.get("/archives/list")
async def get_archives_list(
    request: Request,
    borg_svc: BorgServiceDep,
    templates: TemplatesDep,
    repository_id: str = "",
    db: Session = Depends(get_db),
) -> _TemplateResponse:
    """Get archives list or empty state"""
    if not repository_id or repository_id == "":
        return templates.TemplateResponse(
            request, "partials/archives/empty_state.html", {}
        )

    try:
        repo_id = int(repository_id)
        repository = db.query(Repository).filter(Repository.id == repo_id).first()
        if repository is None:
            raise HTTPException(status_code=404, detail="Repository not found")

        try:
            archives_response = await borg_svc.list_archives(repository)

            processed_archives = []

            if archives_response.archives:
                recent_archives = (
                    archives_response.archives[-10:]
                    if len(archives_response.archives) > 10
                    else archives_response.archives
                )
                recent_archives.reverse()

                for archive in recent_archives:
                    archive_name = archive.name
                    archive_time = (
                        archive.start
                    )  # Use start time as the primary timestamp

                    formatted_time = archive_time
                    if archive_time:
                        try:
                            dt = parse_datetime_string(archive_time)
                            if dt:
                                formatted_time = format_datetime_for_display(dt)
                            else:
                                formatted_time = archive_time
                        except (ValueError, TypeError):
                            pass

                    size_info = ""
                    if archive.original_size is not None:
                        size_bytes = float(archive.original_size)
                        for unit in ["B", "KB", "MB", "GB", "TB"]:
                            if size_bytes < 1024.0:
                                size_info = f"{size_bytes:.1f} {unit}"
                                break
                            size_bytes /= 1024.0

                    processed_archives.append(
                        {
                            "name": archive_name,
                            "formatted_time": formatted_time,
                            "size_info": size_info,
                        }
                    )

            return templates.TemplateResponse(
                request,
                "partials/archives/list_content.html",
                {
                    "repository": repository,
                    "archives": archives_response.archives,
                    "recent_archives": processed_archives,
                },
            )

        except Exception as e:
            logger.error(f"Error listing archives for repository {repo_id}: {e}")
            return templates.TemplateResponse(
                request,
                "partials/archives/error_message.html",
                {
                    "error_message": str(e),
                    "show_help": True,
                },
            )

    except HTTPException:
        raise
    except (ValueError, TypeError):
        return templates.TemplateResponse(
            request, "partials/archives/empty_state.html", {}
        )
    except Exception as e:
        logger.error(f"Unexpected error in list_archives_html: {e}")
        return templates.TemplateResponse(
            request,
            "partials/archives/error_message.html",
            {
                "error_message": "An unexpected error occurred while loading archives.",
                "show_help": False,
            },
        )


@router.post("/{repo_id}/archives/{archive_name}/contents/load-with-spinner")
async def load_archive_contents_with_spinner(
    request: Request,
    repo_id: int,
    archive_name: str,
    templates: TemplatesDep,
    path: str = Form(""),
    db: Session = Depends(get_db),
) -> _TemplateResponse:
    """Show loading spinner then trigger loading actual directory contents"""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    return templates.TemplateResponse(
        request,
        "partials/archives/directory_loading_with_trigger.html",
        {"repository_id": repo_id, "archive_name": archive_name, "path": path},
    )


@router.get("/{repo_id}/archives/{archive_name}/contents")
async def get_archive_contents(
    request: Request,
    repo_id: int,
    archive_name: str,
    borg_svc: BorgServiceDep,
    templates: TemplatesDep,
    path: str = "",
    db: Session = Depends(get_db),
) -> _TemplateResponse:
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    try:
        contents = await borg_svc.list_archive_directory_contents(
            repository, archive_name, path
        )

        return templates.TemplateResponse(
            request,
            "partials/archives/directory_contents.html",
            {
                "repository": repository,
                "archive_name": archive_name,
                "path": path,
                "items": contents,
                "breadcrumb_parts": path.split("/") if path else [],
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            request,
            "partials/common/error_message.html",
            {"error_message": f"Error loading directory contents: {str(e)}"},
        )


@router.get("/{repo_id}/archives/{archive_name}/extract")
async def extract_file(
    repo_id: int,
    archive_name: str,
    file: str,
    archive_manager: ArchiveManagerDep,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")

    try:
        return await archive_manager.extract_file_stream(repository, archive_name, file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
