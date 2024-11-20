import os
import re
import asyncio
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ValidationError
from typing import Callable, Dict, Any
import pybars
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.applications import Starlette
import uvicorn


class Kwame:
    def __init__(self, template_folder='templates', static_folder='static'):
        self.app = Starlette(debug=True)
        self.routes = []
        self.middlewares = []
        self.env = Environment(loader=FileSystemLoader(template_folder))
        self.handlebars = pybars.Compiler()
        self.template_folder = template_folder
        self.static_folder = static_folder

    def add_route(self, path: str, endpoint: Callable, methods: list = ["GET"]):
        """ Register routes dynamically """
        route = Route(path, endpoint, methods=methods)
        self.routes.append(route)

    def add_middleware(self, middleware_class: BaseHTTPMiddleware):
        """ Add middleware to the app """
        self.middlewares.append(middleware_class)

    def create_app(self):
        """ Create the app with the given routes and middlewares """
        for middleware in self.middlewares:
            self.app.add_middleware(middleware)
        self.app.routes.extend(self.routes)
        return self.app

    def render_jinja(self, template_name: str, context: Dict[str, Any]) -> HTMLResponse:
        """ Render Jinja2 templates """
        template = self.env.get_template(template_name)
        return HTMLResponse(template.render(context))

    def render_handlebars(self, template_string: str, context: Dict[str, Any]) -> HTMLResponse:
        """ Render Handlebars templates """
        template = self.handlebars.compile(template_string)
        return HTMLResponse(template(context))

    def json_response(self, data: Dict[str, Any]) -> JSONResponse:
        """ Return a JSON response """
        return JSONResponse(data)


class PydanticRequestModel(BaseModel):
    """ Base Pydantic model for data validation """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_request(cls, request: Request):
        """ Parse and validate request data """
        try:
            return cls.parse_obj(request.json())
        except ValidationError as e:
            raise ValueError(f"Request body validation error: {e}")


class MiddlewareExample(BaseHTTPMiddleware):
    """ Example middleware for logging """
    async def dispatch(self, request: Request, call_next):
        print(f"Request to {request.url.path}")
        response = await call_next(request)
        return response


# Define your controllers

# Controller: Render Jinja2 template
async def home_controller(request: Request):
    data = {
        'title': 'Welcome to Kwame!',
        'message': 'This is a simple example using Jinja2 templates.'
    }
    return kwame.render_jinja('home.html', data)


# Controller: Render Handlebars template
async def handlebars_controller(request: Request):
    handlebars_template = """
    <html>
        <head><title>{{title}}</title></head>
        <body>
            <h1>{{message}}</h1>
        </body>
    </html>
    """
    data = {
        'title': 'Handlebars Rendering in Kwame',
        'message': 'This message is rendered using Handlebars on the server.'
    }
    return kwame.render_handlebars(handlebars_template, data)


# Controller: Handle API endpoint with Pydantic validation
class UserModel(PydanticRequestModel):
    username: str
    email: str

async def api_user_controller(request: Request):
    try:
        user_data = await UserModel.from_request(request)
        return kwame.json_response({"message": "User validated", "user": user_data.dict()})
    except ValueError as e:
        return kwame.json_response({"error": str(e)})


# Initialize Kwame framework instance
kwame = Kwame(template_folder="templates", static_folder="static")

# Register routes
kwame.add_route('/', home_controller, methods=["GET"])
kwame.add_route('/handlebars', handlebars_controller, methods=["GET"])
kwame.add_route('/api/user', api_user_controller, methods=["POST"])

# Add middleware
kwame.add_middleware(MiddlewareExample)

# Create the app and run with Uvicorn
app = kwame.create_app()

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
