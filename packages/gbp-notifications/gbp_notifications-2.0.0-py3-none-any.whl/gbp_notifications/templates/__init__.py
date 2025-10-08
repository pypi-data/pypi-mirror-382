"""GBP Notifications Template handling"""

import typing as t

import jinja2.exceptions
from jinja2 import Environment, PackageLoader, Template, select_autoescape

from gbp_notifications.exceptions import TemplateNotFoundError


def load_template(name: str) -> Template:
    """Load the template with the given name"""
    loader = PackageLoader("gbp_notifications")
    env = Environment(loader=loader, autoescape=select_autoescape(["html", "xml"]))

    try:
        return env.get_template(name)
    except jinja2.exceptions.TemplateNotFound as error:
        raise TemplateNotFoundError(name, error.message) from error


def render_template(template: Template, context: dict[str, t.Any]) -> str:
    """Render the given Template given the context"""
    return template.render(**context)
