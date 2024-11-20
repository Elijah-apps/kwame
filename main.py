import os
import asyncio
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ValidationError
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.applications import Starlette
import uvicorn
import pybars
from starlette.middleware.sessions import SessionMiddleware

# Database setup (SQLAlchemy ORM)
DATABASE_URL = "sqlite:///./test.db"

Base = declarative_base()

# Example model for a user in the SQLite database
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)

# Create database engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Kwame Framework
class Kwame:
    def __init__(self, template_folder='templates', static_folder='static'):
        self.app = Starlette(debug=True)
        self.routes = []
        self.middlewares = []
        self.env = Environment(loader=FileSystemLoader(template_folder))
        self.handlebars = pybars.Compiler()
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.app.add_middleware(SessionMiddleware, secret_key="secret")  # Session middleware
        self.db = SessionLocal()  # Initializing DB session
        
    def add_route(self, path: str, endpoint: callable, methods: list = ["GET"]):
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
        
    def render_jinja(self, template_name: str, context: dict) -> HTMLResponse:
        """ Render Jinja2 templates """
        template = self.env.get_template(template_name)
        return HTMLResponse(template.render(context))

    def render_handlebars(self, template_string: str, context: dict) -> HTMLResponse:
        """ Render Handlebars templates """
        template = self.handlebars.compile(template_string)
        return HTMLResponse(template(context))

    def json_response(self, data: dict) -> JSONResponse:
        """ Return a JSON response """
        return JSONResponse(data)
    
    def get_db(self):
        """ Return DB session """
        db = self.db
        try:
            yield db
        finally:
            db.close()

    def set_session(self, request: Request, key: str, value: str):
        """ Set session data """
        request.session[key] = value

    def get_session(self, request: Request, key: str):
        """ Get session data """
        return request.session.get(key, None)

# Pydantic model for validation
class UserModel(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True

# Example Controller to interact with the database and session
async def home_controller(request: Request):
    username = kwame.get_session(request, 'username')
    data = {'message': f'Hello, {username or "Guest"}!'}
    return kwame.render_jinja('home.html', data)

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

# API Controller to create a user
async def api_create_user(request: Request):
    try:
        user_data = await UserModel.from_request(request)
        db = next(kwame.get_db())
        db_user = User(username=user_data.username, email=user_data.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return kwame.json_response({"message": "User created successfully", "user": user_data.dict()})
    except ValueError as e:
        return kwame.json_response({"error": str(e)})

# Initialize Kwame framework instance
kwame = Kwame(template_folder="templates", static_folder="static")

# Register routes
kwame.add_route('/', home_controller, methods=["GET"])
kwame.add_route('/handlebars', handlebars_controller, methods=["GET"])
kwame.add_route('/api/create_user', api_create_user, methods=["POST"])

# Create the app and run with Uvicorn
app = kwame.create_app()

# Create database tables on startup
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
