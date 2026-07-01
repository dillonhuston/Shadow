# Contributing to ShadowBox

Thank you for your interest in improving ShadowBox! I have completed my primary work on this project for now. I am shifting my focus to polish other projects in my portfolio, so I welcome any community contributions to help keep the project stable and secure.

## Workflow
All contributions should be made via a dedicated **`contribution`** branch to keep the main codebase clean.
1. Create a new branch from `contribution`: `git checkout contribution`
2. Create your feature branch: `git checkout -b feature/your-feature-name`
3. Push your changes and open a Pull Request targeting the `contribution` branch.

## Standards & Best Practices

To keep the codebase clean and maintainable, please follow the following standards I have added:

### 1. PEP 8 & Linting
* Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines.
* Use type hints for all function arguments and return types.
* Keep the code readable and document any complex logic.

### 2. FastAPI & Async Patterns
* **Always use `async/await`**: ShadowBox is designed as an asynchronous system. Please avoid blocking I/O operations (like standard `time.sleep` or synchronous file operations) within route handlers or services.
* **Dependency Injection**: Leverage FastAPI’s `Depends` for database sessions and security handlers. Do not instantiate these manually inside your routes.
* **Service Layer**: Keep your routes "thin." All business logic and database orchestration must reside in the `app/services/` layer.

### 3. Error Handling
* **Do not use `try/except` in routers**: We use a centralized `ServiceError` hierarchy. 
* If a service method encounters an error, it should `raise` the appropriate `ServiceError` (defined in `app/exceptions/exceptions.py`). The global exception handler will automatically catch these and return a consistent JSON response.

### 4. Security
* Never hardcode sensitive information. Always use environment variables.
* Ensure that any new endpoints requiring identity verification use the `JWTHandler` dependency.

---

I’m excited to see how this project grows with your help! If you have any questions about the current architecture, feel free to open an issue before starting your work.
