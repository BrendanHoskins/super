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
- Slack App ([create one at api.slack.com/apps](https://api.slack.com/apps))

### Configuring the Slack App

After creating your app, configure the following in the [Slack API dashboard](https://api.slack.com/apps) so the server can receive events and complete OAuth. Use your **ngrok URL** (e.g. `https://your-name.ngrok-free.app`) as the base for all URLs below.

#### 1. Event Subscriptions

Under **Features → Event Subscriptions**:

- **Enable Events**: Turn On.
- **Request URL**:  
  `https://<your-ngrok-url>/api/slack/events/webhooks`  
  (e.g. `https://your-name.ngrok-free.app/api/slack/events/webhooks`).  
  Slack will send a verification request to this URL; the server responds with the challenge to verify.
- **Subscribe to workspace events**: add at least:
  - `message.channels` – messages in public channels
  - `message.groups` – messages in private channels
  - `message.im` – direct messages
  - `message.mpim` – group DMs
  - `reaction_added` – when an emoji reaction is added
  - `reaction_removed` – when an emoji reaction is removed  

  These align with the app’s filtering (messages and reactions).

#### 2. OAuth & Permissions

Under **Features → OAuth & Permissions** (only **user** scopes are needed; no bot scopes):

- **Redirect URLs**: Add:  
  `https://<your-ngrok-url>/api/slack/oauth/callback`  
  (e.g. `https://your-name.ngrok-free.app/api/slack/oauth/callback`).  
  This must match the URL your backend uses (the app derives it from `NGROK_URL` or `SLACK_REDIRECT_URI` in `.env`).
- **User Token Scopes** (OAuth flow): Add the scopes your app needs. The example `.env` uses:
  - `emoji:read` – list emojis for filter configuration
  - `users:read` – list workspace users for member filters
  - `users:read.email` – user email (if needed)
  - `usergroups:read` – user groups
  - `channels:history`, `groups:history`, `im:history`, `mpim:history` – read message history in channels, private channels, DMs, and group DMs
  - `reactions:read` – read reactions on messages  

  Set the same comma-separated list in `.env` as `SLACK_USER_SCOPES`.

After changing Event Subscriptions or Redirect URLs, reinstall the app to your workspace if prompted.

### Environment Variables

One env file at the repo root. Create it from the example and fill in your Slack and JWT values:

```bash
cp .env.example .env
# Edit .env with your secrets
```

(`make docker-super` will create `.env` from `.env.example` automatically if `.env` is missing.)

### Running with Docker (recommended)

Once `.env` at the repo root is populated:

```bash
make docker-super
```

This will:

- **Scan for open ports** for the backend (from 5000) and frontend (from 3000), then start MongoDB, Flask backend, and Vite frontend. The script prints the **App URL** and **Backend API** to use; the Vite dev server will show the same port so you always open the correct URL.
- If you set `NGROK_URL` and `NGROK_AUTHTOKEN` in `.env`, the stack will also start an **ngrok** container that exposes the backend at your static ngrok domain (for Slack OAuth). The redirect URI is set to `https://{NGROK_URL}/api/slack/oauth/callback` automatically.

You can also run it detached:

```bash
make docker-super-detach
```

#### Ports: override or troubleshoot

To force specific ports instead of auto-selecting:

```bash
BACKEND_PORT=5001 FRONTEND_PORT=3001 make docker-super
```