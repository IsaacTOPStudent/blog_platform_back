# Blog Platform Backend

This is the backend of a blogging platform, built with the Django REST Framework.
It allows for the management of users, posts, comments, and likes, with JWT token-based authentication.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/IsaacTOPStudent/blog_platform_back.git
cd blog_platform_back
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 3.1 Install dev requirements (optional)
```bash
pip install -r requirements-dev.txt
```

### 4. Environment Variables
1. Copy the example file:
   ```bash
   cp example.env .env
   ```
2. Edit the `.env` file with your own settings (secret key, database, etc).

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Run the server
```bash
python manage.py runserver
```

### 8. Run tests
```bash
pytest
```

## API Documentation

- **GET** `/api/schema/` → API schema in OpenAPI format
- **GET** `/api/docs/schema/swagger-ui/` → Interactive documentation (Swagger UI)
- **GET** `/api/docs/schema/redoc/` → Alternative documentation (ReDoc)

## Main Endpoints

### Authentication
- **POST** `/api/users/register/` → User registration
- **POST** `/api/users/login/` → Login (get Token)
- **POST** `/api/users/logout/` → Logout (blacklist token)

### Posts
- **GET** `/api/posts/` → List all posts
- **POST** `/api/posts/` → Create a new post (requires authentication)
- **GET** `/api/posts/{id}/` → View post details 
- **PUT** `/api/posts/{id}/` → Edit a post (requires authentication)
- **DELETE** `/api/posts/{id}/` → Delete a post (requires authentication)

### Comments
- **POST** `/api/posts/{post_id}/comments/` → Create comment on a post (requires authentication)
- **GET** `/api/posts/{post_id}/comments/` → List comments of a post
- **DELETE** `/api/comments/{id}/` → Delete comment (requires authentication)

### Likes
- **POST** `/api/posts/{post_id}/like/` → Like (requires authentication)
- **DELETE** `/api/posts/{post_id}/like/` → Unlike post (requires authentication)
- **GET** `/api/posts/{post_id}/likes/` → List likes of a post

## Author

**Isaac Violet**
