# MongoDB CRUD API

A fast, scalable, and production-ready REST API built with FastAPI and MongoDB for generic JSON object storage with full CRUD operations.

## 🐳 Docker Image

**Available on Docker Hub**: `efexzium/mongodb-crud-api:latest`

```bash
docker pull efexzium/mongodb-crud-api:latest
```

## 🚀 Features

- **Fast & Modern**: Built with FastAPI for high performance
- **Async Operations**: Uses Motor for async MongoDB operations
- **Generic Storage**: Store any JSON-like objects flexibly
- **Complete CRUD**: Create, Read, Update, Delete operations
- **Health Checks**: Built-in health monitoring endpoints
- **Docker Ready**: Containerized for easy deployment
- **Comprehensive Testing**: Full test suite with pytest
- **Type Safe**: Built with Pydantic for data validation

## 📋 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check and database connection status |
| `GET` | `/ping` | Alternative health check endpoint |
| `POST` | `/items` | Create a new item |
| `GET` | `/items` | List all items with pagination |
| `GET` | `/items/{id}` | Get specific item by ID |
| `PUT` | `/items/{id}` | Update existing item |
| `DELETE` | `/items/{id}` | Delete item |

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- MongoDB Atlas account (or local MongoDB)
- Docker (optional, for containerized deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MongoDB-Fast-API
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MongoDB**
   - Update the `MONGO_URI` in [`main.py:14`](main.py:14) with your MongoDB Atlas connection string
   - Ensure your MongoDB database and collection names are correct (default: `mystore`/`items`)

5. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t mongodb-crud-api:latest .
   ```

2. **Run with Docker**
   ```bash
   docker run -d -p 8000:8000 --name mongodb-crud-api mongodb-crud-api:latest
   ```

3. **Or use Docker Compose**
   ```bash
   docker-compose up -d
   ```

The Docker container will be available at `http://localhost:8000`

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest -v

# Run specific test file
pytest test.py -v

# Run Docker-specific tests
pytest test_docker.py -v
```

### Test Coverage

The test suite covers:
- ✅ Health check endpoints
- ✅ Create and retrieve items
- ✅ List items with pagination
- ✅ Update existing items (partial updates)
- ✅ Delete items
- ✅ Error handling and edge cases

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_URI` | Configured in code | MongoDB connection string |
| `DB_NAME` | `mystore` | Database name |
| `COLLECTION` | `items` | Collection name |

### MongoDB Setup

1. **Create MongoDB Atlas Cluster**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a free cluster
   - Create a database user with read/write permissions
   - Get your connection string

2. **Update Connection String**
   ```python
   MONGO_URI = "mongodb+srv://username:password@cluster-url.mongodb.net/?retryWrites=true&w=majority"
   ```

## 📝 API Usage Examples

### Create an Item

```bash
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Product",
    "price": 29.99,
    "category": "electronics",
    "in_stock": true
  }'
```

### Get All Items

```bash
curl "http://localhost:8000/items?limit=10&skip=0"
```

### Get Specific Item

```bash
curl "http://localhost:8000/items/item-id-here"
```

### Update Item

```bash
curl -X PUT "http://localhost:8000/items/item-id-here" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 24.99,
    "in_stock": false
  }'
```

### Delete Item

```bash
curl -X DELETE "http://localhost:8000/items/item-id-here"
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "MongoDB Atlas ready 🚀"
}
```

## 🐳 Docker Commands

### Using Docker Hub Image

```bash
# Pull from Docker Hub
docker pull efexzium/mongodb-crud-api:latest

# Run container
docker run -d -p 8000:8000 --name mongodb-crud-api efexzium/mongodb-crud-api:latest

# Check logs
docker logs mongodb-crud-api

# Stop container
docker stop mongodb-crud-api

# Remove container
docker rm mongodb-crud-api
```

### Build and Run (Local)

```bash
# Build image
docker build -t mongodb-crud-api:latest .

# Run container
docker run -d -p 8000:8000 --name mongodb-crud-api mongodb-crud-api:latest
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View status
docker-compose ps

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### Quick Start with Docker Hub

```bash
# 1. Pull the image
docker pull efexzium/mongodb-crud-api:latest

# 2. Run the container
docker run -d \
  -p 8000:8000 \
  --name mongodb-crud-api \
  -e MONGO_URI="mongodb+srv://your-username:your-password@cluster-url.mongodb.net/?retryWrites=true&w=majority" \
  efexzium/mongodb-crud-api:latest

# 3. Test the API
curl http://localhost:8000/health
```

## 📊 Production Deployment

### Prerequisites

- MongoDB Atlas cluster or production MongoDB instance
- Domain name and SSL certificate
- Reverse proxy (Nginx, Apache, etc.)

### Steps

1. **Update MongoDB URI** in production configuration
2. **Set up environment variables** for production
3. **Configure reverse proxy** for SSL termination
4. **Set up monitoring** and logging
5. **Configure backup** strategy for MongoDB

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔍 Monitoring

### Health Check

The `/health` endpoint provides:
- Application status
- Database connection status
- Response time metrics

### Logging

The application includes:
- Request logging
- Error logging
- Database operation logging

### Metrics

Monitor:
- Request count and response times
- Database connection pool status
- Error rates

## 🛡️ Security Considerations

- **MongoDB Connection**: Use SSL/TLS for MongoDB connections
- **Environment Variables**: Store sensitive data in environment variables
- **Input Validation**: Pydantic models provide input validation
- **CORS**: Configure CORS policies for your frontend
- **Rate Limiting**: Implement rate limiting for production

## 🚀 Development Workflow

1. **Feature Development**
   ```bash
   # Create feature branch
   git checkout -b feature/new-feature
   
   # Make changes
   # Test locally
   pytest -v
   
   # Test with Docker
   docker build -t test-api:latest .
   docker run -d -p 8001:8000 --name test-api test-api:latest
   pytest test_docker.py -v
   ```

2. **Code Quality**
   ```bash
   # Run linting
   flake8 .
   
   # Format code
   black .
   
   # Run type checking
   mypy .
   ```

## 📈 Performance Optimization

### Database Optimization
- Index frequently queried fields
- Use appropriate MongoDB collection settings
- Monitor query performance

### Application Optimization
- Use connection pooling
- Implement caching for frequently accessed data
- Optimize pagination parameters

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with:
   - Detailed description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment information

## 🔄 Changelog

### v1.0.0
- Initial release
- Complete CRUD operations
- Docker support
- Comprehensive test suite
- Health monitoring endpoints
- Error handling and validation

---

**Built with ❤️ using FastAPI, MongoDB, and Docker**