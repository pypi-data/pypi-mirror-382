from __future__ import annotations

from .loader import render_template


def render_entity(class_name: str) -> str:
    """Return the template for a domain entity."""
    return render_template("entity.py.j2", subfolder="domain", class_name=class_name)


def render_repository_interface(
    class_name: str,
    entity_name: str,
    entity_file: str,
) -> str:
    """Return the template for a repository interface."""
    return render_template(
        "repository_interface.py.j2",
        subfolder="domain",
        class_name=class_name,
        entity_name=entity_name,
        entity_file=entity_file,
    )


def render_service_interface(class_name: str) -> str:
    """Return the template for a service interface."""
    return render_template(
        "service_interface.py.j2", subfolder="domain", class_name=class_name
    )


def render_interactor(class_name: str, entity_name: str, entity_file: str) -> str:
    """Return the template for an interactor."""
    return render_template(
        "interactor.py.j2",
        subfolder="domain",
        class_name=class_name,
        entity_name=entity_name,
        entity_file=entity_file,
    )


def render_mediator(class_name: str) -> str:
    """Return the template for a mediator."""
    return render_template("mediator.py.j2", subfolder="domain", class_name=class_name)


def render_infrastructure_repository(
    impl_class: str,
    interface_class_name: str,
    interface_file_name: str,
    entity_name: str,
    entity_file: str,
) -> str:
    """Return the template for a repository implementation."""
    return render_template(
        "repository_impl.py.j2",
        subfolder="infrastructure",
        impl_class=impl_class,
        interface_class_name=interface_class_name,
        interface_file_name=interface_file_name,
        entity_name=entity_name,
        entity_file=entity_file,
    )


def render_infrastructure_service(
    impl_class: str,
    interface_class_name: str,
    interface_file_name: str,
) -> str:
    """Return the template for a service implementation."""
    return render_template(
        "service_impl.py.j2",
        subfolder="infrastructure",
        impl_class=impl_class,
        interface_class_name=interface_class_name,
        interface_file_name=interface_file_name,
    )

def render_web_package_init() -> str:
    """Return the template for web/__init__.py"""
    return render_template("__init__.py.j2", subfolder="web")


def render_fastapi_app(project_name: str) -> str:
    """Return the template for web/app.py"""
    return render_template("app.py.j2", subfolder="web", project_name=project_name)


def render_fastapi_routes_init() -> str:
    """Return the template for web/routes/__init__.py"""
    return render_template("routes_init.py.j2", subfolder="web")


def render_fastapi_health_route() -> str:
    """Return the template for web/routes/health.py"""
    return render_template("health_route.py.j2", subfolder="web")


def render_fastapi_dependencies() -> str:
    """Return the template for web/dependencies.py"""
    return render_template("dependencies.py.j2", subfolder="web")


def render_fastapi_main(project_name: str) -> str:
    """Return the template for presentation/web/main.py"""
    return render_template("main.py.j2", subfolder="web", project_name=project_name)


def render_standard_main(project_name: str) -> str:
    """Return the template for main.py (standard project with CLI)"""
    return render_template(
        "main_standard.py.j2", subfolder="project", project_name=project_name
    )


def render_fastapi_project_main(project_name: str) -> str:
    """Return the template for main.py (FastAPI project with Web and CLI)"""
    return render_template(
        "main_fastapi.py.j2", subfolder="project", project_name=project_name
    )


def render_pydantic_models_init() -> str:
    """Return the template for web/models/__init__.py"""
    return render_template("models_init.py.j2", subfolder="web")


def render_pydantic_user_models() -> str:
    """Return the template for web/models/user_models.py"""
    return render_template("user_models.py.j2", subfolder="web")


def render_fastapi_user_route() -> str:
    """Return the template for web/routes/users.py"""
    return render_template("users_route.py.j2", subfolder="web")


def render_fastapi_router(resource_name: str, resource_file: str, project_name: str) -> str:
    """Return the template for a FastAPI router"""
    return render_template(
        "router.py.j2",
        subfolder="web",
        resource_name=resource_name,
        resource_file=resource_file,
        project_name=project_name,
    )
