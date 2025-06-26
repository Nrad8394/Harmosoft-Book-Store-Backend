# Harmosoft Book Store Backend

A comprehensive e-commerce backend solution for educational book stores and stationery management, built with Django REST Framework. This system provides robust APIs for managing products, orders, payments, user accounts, and organizational structures.

## 🚀 Features

### Core Functionality
- **Product Management**: Complete inventory system for books, stationery, and educational materials
- **Order Processing**: Advanced order management with tracking capabilities
- **Payment Integration**: Multiple payment gateways including M-Pesa and Stripe
- **User Management**: Custom user authentication with organizational support
- **Real-time Updates**: WebSocket support for live order tracking
- **Admin Interface**: Enhanced Django admin with Jazzmin theming

### Key Modules
- **Products**: Item catalog with category management and image handling
- **Orders**: Order lifecycle management with status tracking
- **Payments**: Secure payment processing with multiple gateway support
- **User Manager**: Custom user authentication and organization management
- **Order Tracking**: Real-time order status updates
- **Adverts**: Advertisement and promotional content management

## 🛠 Technology Stack

- **Backend**: Django 5.0.7 + Django REST Framework 3.15.2
- **Database**: MySQL 8.0 (with PostgreSQL support)
- **Authentication**: JWT tokens with django-allauth integration
- **Real-time**: Django Channels for WebSocket support
- **Payments**: M-Pesa (django-daraja) and Stripe integration
- **Containerization**: Docker with docker-compose
- **Web Server**: Nginx + Gunicorn
- **Image Processing**: Pillow for image optimization
- **ML Features**: Scikit-learn for product clustering

## 📋 Prerequisites

- Python 3.8+
- Docker and Docker Compose
- MySQL 8.0 or PostgreSQL
- Node.js (for frontend integration)

## 🔧 Installation

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Harmosoft-Book-Store-Backend.git
   cd Harmosoft-Book-Store-Backend/hbs
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Configure your `.env` file with:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database Configuration
   DB_NAME=hbs_db
   DB_USER=hbs_user
   DB_PASSWORD=hbs_password
   DB_HOST=db
   DB_PORT=3306
   
   # Payment Gateway Keys
   MPESA_CONSUMER_KEY=your-mpesa-consumer-key
   MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
   STRIPE_PUBLIC_KEY=your-stripe-public-key
   STRIPE_SECRET_KEY=your-stripe-secret-key
   ```

3. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: http://localhost/api/
   - Admin Panel: http://localhost/admin/

### Manual Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   cd hbs
   pip install -r requirements.txt
   ```

3. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Populate initial data**
   ```bash
   python populate_orgs.py
   python populate_items.py
   python populate_stationary.py
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

## 📚 API Documentation

### Authentication Endpoints
```
POST /api/auth/login/          # User login
POST /api/auth/register/       # User registration
POST /api/auth/logout/         # User logout
POST /api/auth/refresh/        # Refresh JWT token
```

### Product Endpoints
```
GET    /api/products/          # List all products
POST   /api/products/          # Create new product
GET    /api/products/{id}/     # Get product details
PUT    /api/products/{id}/     # Update product
DELETE /api/products/{id}/     # Delete product
```

### Order Endpoints
```
GET    /api/orders/            # List user orders
POST   /api/orders/            # Create new order
GET    /api/orders/{id}/       # Get order details
PUT    /api/orders/{id}/       # Update order status
```

### Payment Endpoints
```
POST   /api/payments/mpesa/    # Process M-Pesa payment
POST   /api/payments/stripe/   # Process Stripe payment
GET    /api/payments/{id}/     # Get payment status
```

## 🔐 Authentication

The system uses JWT (JSON Web Tokens) for authentication with the following features:

- **Custom User Model**: Extended user model with organizational support
- **Social Authentication**: Google and Apple OAuth integration
- **Email Verification**: Optional email verification for new accounts
- **Phone Number Support**: International phone number validation

## 💳 Payment Integration

### M-Pesa Integration
- STK Push payments
- Payment status callbacks
- Transaction verification
- Automatic reconciliation

### Stripe Integration
- Credit/Debit card processing
- Webhook handling
- Refund management
- Payment intent tracking

## 📱 Real-time Features

The application includes WebSocket support for:
- Live order status updates
- Real-time payment notifications
- Inventory level alerts
- Admin dashboard updates

## 🗂 Project Structure

```
hbs/
├── adverts/              # Advertisement management
├── hbs/                  # Main Django settings
├── media/                # User uploaded files
├── nginx/                # Nginx configuration
├── order/                # Order management
├── order_tracking/       # Order tracking system
├── paymentsApp/          # Payment processing
├── products/             # Product catalog
├── userManager/          # User authentication
├── docker-compose.yml    # Docker configuration
├── Dockerfile           # Docker build instructions
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── populate_*.py        # Data seeding scripts
```

## 🚀 Deployment

### Production Deployment

1. **Environment Configuration**
   ```env
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   ```

2. **Database Migration**
   ```bash
   python manage.py migrate --settings=hbs.settings.production
   ```

3. **Static Files Collection**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Docker Production Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode flag | Yes |
| `ALLOWED_HOSTS` | Allowed host domains | Yes |
| `DATABASE_URL` | Database connection string | Yes |
| `MPESA_CONSUMER_KEY` | M-Pesa API consumer key | No |
| `MPESA_CONSUMER_SECRET` | M-Pesa API consumer secret | No |
| `STRIPE_PUBLIC_KEY` | Stripe public key | No |
| `STRIPE_SECRET_KEY` | Stripe secret key | No |

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test products
python manage.py test orders
python manage.py test paymentsApp
```

## 📊 Monitoring and Logging

- **Error Tracking**: Integrated logging for all modules
- **Performance Monitoring**: Database query optimization
- **Payment Logs**: Detailed payment transaction logs
- **User Activity**: Comprehensive user action logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

For support and questions:
- Create an issue on GitHub
- Email: support@harmosoft.com
- Documentation: [Wiki](https://github.com/your-username/Harmosoft-Book-Store-Backend/wiki)

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added M-Pesa integration
- **v1.2.0** - Enhanced order tracking
- **v1.3.0** - WebSocket real-time features

---

**Made with ❤️ by the Harmosoft Team**
