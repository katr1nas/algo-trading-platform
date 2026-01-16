# Full-Stack Algorithmic Trading Platform

A distributed system for quantitative trading, featuring a high-performance asynchronous backend and a reactive web dashboard. The platform integrates strategy development, historical backtesting, and real-time monitoring.

---

## System Architecture

The project is architected as a decoupled full-stack application, ensuring scalability and ease of deployment via containerization.

### Backend (Python/FastAPI)
* **Asynchronous API:** Built with FastAPI for high-throughput data handling.
* **Database Management:** PostgreSQL integration using SQLAlchemy ORM and **Alembic** for schema migrations.
* **Domain Logic:** Structured into dedicated modules for `indicators`, `strategies`, and `features` engineering.
* **ML Integration:** Dedicated `ml` and `models` directories for integrating predictive analytics.

### Frontend (Vue.js)
* **Reactive Dashboard:** Developed with Vue.js to provide real-time visualization of trading signals and portfolio performance.
* **State Management:** Efficient handling of live market data streams.

### Infrastructure
* **Containerization:** Full **Docker** support for reproducible environments.
* **Backtesting Engine:** Isolated core for evaluating strategies against historical datasets.

## Technical Stack
* **Backend:** Python 3.10+, FastAPI, SQLAlchemy, Alembic, Pydantic.
* **Frontend:** Vue.js, Vite/Webpack.
* **Data Science:** Pandas, NumPy, Scikit-learn (in `ml` modules).
* **DevOps:** Docker, Docker Compose.

## Project Structure
```text
├── backend/
│   ├── app/                # Main FastAPI application core
│   │   ├── api/            # REST API endpoints
│   │   ├── core/           # Configuration and security
│   │   ├── db/             # Database connection and session management
│   │   ├── ml/             # Machine Learning pipelines
│   │   └── models/         # Database models (SQLAlchemy)
│   ├── indicators/         # Technical analysis libraries
│   ├── migrations/         # Alembic database migration scripts
│   ├── strategies/         # Quantitative trading algorithms
│   └── backtester/         # Strategy validation engine
├── frontend/               # Vue.js application
└── Dockerfile              # Deployment configuration
```


Development Status: Alpha

Current focus is on finalizing the Alembic migration flow and integrating the Vue.js frontend with the live FastAPI websocket streams for real-time ticker updates.
Quick Start

Environment: Ensure you have Docker and Python 3.10+ installed.
Backend Setup:
```Bash

cd backend
pip install -r requirements.txt
alembic upgrade head
python app/main.py
```

Frontend Setup:
```Bash
cd frontend
npm install
npm run dev
```

Author: Serghei Barladean
