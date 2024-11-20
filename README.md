# Kwame - A Powerful Python Backend Framework

Kwame is a high-performance, bare-metal backend framework that combines the flexibility and simplicity of Python with powerful features like template rendering with **Jinja2** and **Handlebars**, **session management**, and an **SQLite ORM manager** for seamless database interactions. Designed with scalability and performance in mind, Kwame empowers developers to quickly build robust, modern web applications.

## Features

### 1. **Template Rendering**
   - **Jinja2**: Render HTML templates with powerful templating features.
   - **Handlebars**: Render dynamic content with Handlebars templating engine for a more JavaScript-like syntax.
   - Flexibility to choose between Jinja2 and Handlebars based on your needs.

### 2. **Session Management**
   - **Secure Session Handling**: Built-in middleware for managing sessions using secure cookies.
   - Set and retrieve session data, such as user authentication state, across requests.

### 3. **SQLite ORM Manager**
   - **SQLAlchemy ORM**: Easy-to-use object-relational mapping with support for complex database queries.
   - **SQLite Database Integration**: Kwame comes with an inbuilt SQLite ORM manager to interact with databases effortlessly.
   - Create, read, update, and delete (CRUD) operations with support for automatic table creation.

### 4. **Pydantic Validation**
   - Automatically validate incoming data with **Pydantic** models for type safety and error handling.
   - Strong integration with the request data for enhanced safety.

### 5. **Asynchronous Support**
   - Built-in asynchronous request handling for fast, non-blocking responses.
   - Perfect for handling real-time applications or I/O-bound tasks.

### 6. **Middleware Support**
   - Easy to add custom middleware for request/response processing.
   - Included session middleware and can be extended for other use cases like authentication, logging, etc.

### 7. **Lightweight and Fast**
   - Minimal setup and lightweight code structure, enabling rapid development without sacrificing performance.
   - Designed to be intuitive and developer-friendly, with clear patterns and best practices.

### 8. **Flexible Routing**
   - Dynamic route registration, allowing you to map HTTP methods to specific functions with flexible routing patterns.
   - Supports both synchronous and asynchronous route handlers.

## Installation

To get started with Kwame, simply clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/kwame.git
cd kwame
pip install -r requirements.txt
