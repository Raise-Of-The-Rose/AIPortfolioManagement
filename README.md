# AI Portfolio Management System

An intelligent portfolio management application that leverages AI to provide real-time market analysis, trading recommendations, and portfolio optimization.

## Features

- **🤖 AI-Powered Recommendations**: Machine learning engine providing intelligent trading recommendations
- **📊 Real-Time Dashboard**: Monitor your portfolio performance with live market data
- **💬 AI Chatbot**: Interactive chatbot for market insights and portfolio advice
- **🔐 Secure Authentication**: User authentication with secure credential management
- **📈 Market Analysis**: Comprehensive stock analysis and market trends
- **💼 Portfolio Management**: Track and optimize your investment portfolio
- **🎨 Modern UI**: Responsive design built with React and Tailwind CSS

## Tech Stack

### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **PostCSS** - CSS processing

### Backend
- **Python** - Core backend language
- **FastAPI/Flask** - Web framework (see main.py)
- **SQLite/PostgreSQL** - Database
- **Pandas** - Data analysis and manipulation
- **NumPy** - Numerical computing

## Project Structure

```
AIPortfolioManagement/
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable React components
│   │   ├── pages/          # Page components
│   │   ├── context/        # Context API for state management
│   │   ├── lib/            # Utility functions and API calls
│   │   └── App.tsx         # Main app component
│   └── package.json        # Frontend dependencies
│
├── backend/
│   ├── main.py             # Application entry point
│   ├── ai_engine.py        # AI recommendation engine
│   ├── market_data.py      # Market data fetching
│   ├── trading.py          # Trading logic
│   ├── database.py         # Database operations
│   ├── auth.py             # Authentication logic
│   ├── chatbot.py          # AI chatbot functionality
│   ├── models.py           # Data models
│   └── requirements.txt    # Python dependencies
│
└── README.md               # This file
```

## Getting Started

### Prerequisites
- **Node.js** (v16 or higher) for frontend
- **Python** (v3.9 or higher) for backend
- **npm** or **yarn** for package management

### Installation

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd frontend
npm install
# or
yarn install
```

### Running the Application

#### Start Backend Server
```bash
cd backend
python main.py
```
The backend will run on `http://localhost:8000` (or configured port)

#### Start Frontend Development Server
```bash
cd frontend
npm run dev
# or
yarn dev
```
The frontend will run on `http://localhost:5173` (Vite default)

## Key Components

### Frontend Pages
- **Dashboard** - Overview of portfolio performance and market summary
- **Portfolio** - Detailed portfolio holdings and allocation
- **Market** - Real-time market data and stock information
- **Chat** - AI chatbot interface for insights
- **Stock Detail** - In-depth analysis of individual stocks
- **Login** - User authentication page

### Backend Modules
- **ai_engine.py** - Core AI logic for generating trading recommendations
- **market_data.py** - Integration with market data providers
- **trading.py** - Order execution and trading operations
- **chatbot.py** - Natural language processing for chatbot
- **database.py** - Database schema and operations
- **auth.py** - User authentication and authorization

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```
DATABASE_URL=sqlite:///portfolio.db
API_KEY=your_market_data_api_key
JWT_SECRET=your_jwt_secret
```

For the frontend, create `.env` in the frontend directory:
```
VITE_API_URL=http://localhost:8000
```

## API Endpoints

Key backend endpoints:
- `GET /api/portfolio` - Get user portfolio
- `GET /api/market/stocks` - Get market data
- `POST /api/trades` - Execute a trade
- `GET /api/recommendations` - Get AI recommendations
- `POST /api/chat` - Send message to chatbot

## Development

### Frontend Development
- Components are in `src/components/`
- Pages are in `src/pages/`
- Global state managed via Context API (`src/context/`)
- API utilities in `src/lib/api.ts`

### Backend Development
- Add new endpoints in `main.py`
- Update database models in `models.py`
- Extend AI logic in `ai_engine.py`

## Contributing

1. Create a feature branch (`git checkout -b feature/AmazingFeature`)
2. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
3. Push to the branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

**Last Updated**: May 2026
