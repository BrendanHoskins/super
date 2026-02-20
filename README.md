# Super

A Slack integration platform that enables users to filter and monitor Slack messages based on customizable team member and emoji configurations.

## Overview

Super allows users to connect their Slack workspace and configure personalized filters to receive only relevant messages. Users can select specific team members and emojis to monitor, and the platform will process incoming Slack events to surface messages that match their criteria.

## Features

- **Slack Integration**: OAuth-based connection to Slack workspaces
- **Customizable Filters**: Configure which team members and emojis to monitor
- **Message Dashboard**: View filtered messages in a centralized interface
- **Real-time Processing**: Webhook-based event processing for instant message updates
- **User Authentication**: Secure JWT-based authentication with refresh tokens

## Tech Stack

### Frontend

- **React 18** - Modern UI library for building interactive interfaces
- **Material-UI (MUI)** - Component library for consistent, accessible UI design
- **React Router v6** - Client-side routing with protected routes
- **Axios** - HTTP client with interceptors for token management
- **Emoji Picker Libraries** - Multiple emoji libraries for rich emoji selection UI

### Backend

- **Flask** - Lightweight Python web framework
- **MongoDB** - NoSQL database for flexible document storage
- **MongoEngine** - ODM (Object Document Mapper) for MongoDB
- **Flask-JWT-Extended** - JWT token management with refresh token support
- **Slack SDK** - Official Slack API client for Python
- **Boto3** - AWS SDK (for potential cloud storage/file handling)

## Architecture

### Project Structure

```
super/
├── client/                 # React frontend application
│   ├── src/
│   │   ├── api/           # API client configuration
│   │   ├── components/    # React components
│   │   ├── routes/        # Route protection logic
│   │   └── services/      # Frontend services (auth)
│   └── package.json
│
└── server/                # Flask backend application
    ├── api/               # API route blueprints
    │   ├── auth_routes.py
    │   ├── integrations_routes.py
    │   ├── messages_routes.py
    │   └── slack/         # Slack-specific routes
    ├── models/            # Database models
    │   ├── user/
    │   └── slack/
    └── services/          # Business logic
        ├── auth/
        └── slack/
```

## Technical Decisions & Rationale

### Authentication: JWT with Refresh Tokens in HttpOnly Cookies

**Why**:

- **Security**: Refresh tokens stored in HttpOnly cookies cannot be accessed via JavaScript, preventing XSS attacks
- **User Experience**: Automatic token refresh via Axios interceptors provides seamless authentication without user intervention
- **Scalability**: Stateless JWT tokens allow horizontal scaling without shared session storage

**Implementation**:

- Access tokens sent in Authorization header (short-lived)
- Refresh tokens stored in HttpOnly cookies (30-day expiration)
- Automatic refresh on 401 responses via Axios response interceptor
- Token blacklist for logout functionality

### Database: MongoDB with MongoEngine ODM

**Why**:

- **Flexible Schema**: Third-party integrations (like Slack) have varying data structures that benefit from document-based storage
- **Nested Data**: Embedded documents allow storing complex integration configurations (OAuth state, installation details, team configurations) within user documents
- **Rapid Development**: Schema-less design enables quick iteration on integration models without migrations

**Implementation**:

- User documents contain a `MapField` of `ThirdPartyIntegration` embedded documents
- Each integration type (Slack) extends `ThirdPartyIntegration` with integration-specific fields
- Embedded documents for OAuth state, installation details, and user configurations

### API Architecture: Flask Blueprints

**Why**:

- **Modularity**: Separates concerns by feature domain (auth, integrations, messages, Slack)
- **Maintainability**: Each blueprint is self-contained, making the codebase easier to navigate and test
- **Scalability**: New integrations can be added as separate blueprints without modifying existing code

**Implementation**:

- Blueprints registered with URL prefixes (`/api/auth`, `/api/integrations`, `/api/messages`, `/api/slack`)
- Slack-specific routes further organized into sub-blueprints (OAuth, events, usage)

### Frontend: React Router with Route Protection

**Why**:

- **Security**: Prevents unauthorized access to protected routes at the component level
- **User Experience**: Automatic redirects to login for unauthenticated users
- **Separation of Concerns**: Public routes (login, register) vs private routes (messages, integrations)

**Implementation**:

- `PrivateRoute` component wraps protected routes and checks authentication
- `PublicRoute` component handles public routes and redirects authenticated users
- Layout component provides consistent UI structure for authenticated pages

### API Client: Axios with Interceptors

**Why**:

- **Centralized Token Management**: All API requests automatically include access tokens
- **Automatic Refresh**: Transparent token refresh on expiration without user action
- **Error Handling**: Centralized error handling and redirect logic for authentication failures

**Implementation**:

- Request interceptor adds Authorization header with access token
- Response interceptor catches 401 errors and attempts token refresh
- Failed refresh redirects to login page

### Event Processing: Webhook-based Architecture

**Why**:

- **Real-time Updates**: Immediate processing of Slack events without polling
- **Efficiency**: Only processes events when they occur, reducing API calls
- **Scalability**: Event-driven architecture handles high-volume message streams

**Implementation**:

- Slack webhook endpoint verifies request signatures for security
- Events processed asynchronously to avoid blocking webhook responses
- User-specific filtering based on team member and emoji configurations

### Data Model: Embedded Documents for Integrations

**Why**:

- **Data Locality**: All integration data stored with user document, reducing queries
- **Atomic Updates**: User and integration updates can be atomic operations
- **Flexibility**: Each integration type can have unique embedded document structures

**Implementation**:

- `SlackIntegration` extends `ThirdPartyIntegration` base class
- Contains embedded documents for OAuth state, installation details, team configurations, and emoji configurations
- Allows multiple integrations per user via `MapField`

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB instance
- Slack App credentials (Client ID, Client Secret, Signing Secret)

### Environment Variables

Create env files from the provided examples and fill in your Slack details:

- Copy `server/.env.example` to `server/.env` and update the Slack and JWT values.
- Copy `client/.env.example` to `client/.env` if you want to override the default backend URL.

```bash
cp server/.env.example server/.env
cp client/.env.example client/.env
```

### Running with Docker (recommended)

Once your `.env` files are populated:

```bash
make docker-super
```

This will:

- Start a local MongoDB instance in Docker.
- **Auto-select the first open ports** for the backend (default 5000) and frontend (default 3000). If 5000 or 3000 are in use, it will try 5001, 5002, … and 3001, 3002, … and print the URLs when it starts.
- Build and run the Flask backend and React frontend.

You can also run it detached:

```bash
make docker-super-detach
```

#### Ports: override or troubleshoot

To force specific ports instead of auto-selecting:

```bash
BACKEND_PORT=5001 FRONTEND_PORT=3001 make docker-super
```

**View what’s using a port (macOS/Linux):**

```bash
lsof -i :5000
```

**Kill the process using a port:**

```bash
kill -9 $(lsof -ti :5000)
```

Replace `5000` with the port you care about. Use `sudo` if the process is owned by another user.

### Manual Installation (without Docker)

#### Backend

```bash
cd server
pip install -r requirements.txt
python app.py
```

#### Frontend

```bash
cd client
npm install
npm start
```

The application will be available at `http://localhost:3000`.

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive access token
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout and invalidate tokens

### Integrations

- `GET /api/integrations/connected-integrations` - Get user's connected integrations
- `POST /api/slack/oauth/install` - Initiate Slack OAuth flow
- `POST /api/slack/oauth/uninstall` - Disconnect Slack integration

### Messages

- `GET /api/messages/get-messages` - Get filtered messages for authenticated user

### Slack Webhooks

- `POST /api/slack/events/webhooks` - Receive Slack event webhooks

## Development

### Running Tests

```bash
# Backend
cd server
python -m pytest

# Frontend
cd client
npm test
```

### Code Style

- Python: Follow PEP 8 guidelines
- JavaScript: ESLint configuration extends `react-app` preset

## Security Considerations

- **CSRF Protection**: Currently disabled for development (`JWT_COOKIE_CSRF_PROTECT = False`). Enable in production.
- **HTTPS**: Set `JWT_COOKIE_SECURE = True` in production to ensure cookies are only sent over HTTPS
- **Token Expiration**: Access tokens are short-lived; refresh tokens expire after 30 days
- **Webhook Verification**: All Slack webhooks are verified using signature verification

## Future Enhancements

- Additional third-party integrations (Teams, Discord, etc.)
- Advanced filtering options (keywords, channels, time ranges)
- Message analytics and insights
- Real-time notifications
- Message search and export functionality

## License

[Your License Here]
