# ShadowBox

![ShadowBox Demo](demo.gif)


**ShadowBox API**

I have completed my primary work on this project for now. The API is functional, stable, and uses a modular service-oriented architecture with global error handling.

I am shifting my focus to polish other projects in my portfolio, so you are more than welcome to contribute! If you'd like to help, please see the CONTRIBUTING.md file for guidelines on how to submit changes and maintain the project's standards.

ShadowBox provides a hardened API for storing files with AES-256 encryption at rest. Built for security, the system ensures files are encrypted before hitting the disk and only decrypted upon authorized download. Designed as a modular service, it is perfect for deployment on local networks, private servers, or Raspberry Pi environments.




## Architecture & Security
- SEncrypted Storage: Implements AES-256 encryption using the cryptography library.
-Modular Design: Built with a clean separation of concerns using Service-Oriented Architecture (SOA).
- Secure Auth: Stateless authentication using JWT (JSON Web Tokens) with OAuth2 bearer flow.
- Dependency Injection: Clean API design using FastAPI dependency injection for DB sessions and security handlers.

## Tech Stack
- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: Dart (replaceable with any frontend)
- **Security**: AES-256, PyJWT, Passlib(Bcrypt), Cryptography(Fernet)
- **Database**: SQLite (swappable)
- **Infrastructure**: Docker, Uvicorn

## QUICK START (Docker)


### Requirements
- Python 3.8+ (for backend)
- Dart (optional, for frontend)
- OR Docker (easiest setup)



```bash
# Clone the repository
git clone [https://github.com/dillionhuston/Shadow.git](https://github.com/dillionhuston/Shadow.git)
cd Shadow

# Build the container
docker build -t shadowbox-api .

# Run the container
docker run -p 8000:8000 --env-file .env shadowbox-api
```
## API Documentation

Once running, navigate to http://localhost:8000/docs to view the auto-generated Swagger/OpenAPI documentation. You can test endpoints (signup, login, upload, dashboard) directly from there.


## Development Setup

- Environment: Create a .env file with SECRET_KEY, ALGORITHM, DATABASE_URL, and UPLOAD_FILE_PATH.

- Dependencies: pip install -r requirements.txt

- Run Dev: uvicorn main:app --reload

- Testing: To be added.

## Why ShadowBox?

- Zero Third-Party Tracking: Full sovereignty over your file system.

- Production-Grade Auth: JWT-based identity management.

- Extensible: Built with a modular router/service pattern, making it easy to add new storage backends or features.



## License
MIT—free to use, modify, and share
