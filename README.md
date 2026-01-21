# Reddit Review Extractor

A full-stack application for extracting, analyzing, and displaying product reviews from Reddit. This project combines a Python backend for data extraction and processing with a TypeScript/React frontend for visualization and user interaction.

## Features

- **Reddit Data Extraction**: Scrape product reviews and discussions from Reddit using the Reddit API
- **Smart Parsing**: Extract relevant review information including sentiment, product mentions, and user opinions
- **Real-time Processing**: Process and filter reviews in real-time based on user queries
- **Interactive Dashboard**: View and filter extracted reviews through an intuitive web interface
- **Data Visualization**: Analyze review trends, sentiment distribution, and product popularity
- **Search & Filter**: Find specific reviews by keyword, product, sentiment, or date range

## Project Structure

```
Reddit_review_extractor/
├── backend/              # Python Flask/FastAPI backend
│   ├── src/
│   ├── requirements.txt
│   └── config.py
├── frontend/             # TypeScript/React frontend
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 14+** and **npm** or **yarn** (for frontend)
- **Reddit API credentials** (PRAW client ID and secret)
- **Git**

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Reddit API credentials:
   - Create a `.env` file in the backend directory
   - Add your Reddit API credentials:
     ```
     REDDIT_CLIENT_ID=your_client_id
     REDDIT_CLIENT_SECRET=your_client_secret
     REDDIT_USER_AGENT=your_user_agent
     ```

5. Start the backend server:
   ```bash
   python app.py
   ```
   The server will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (if needed) for API configuration:
   ```
   REACT_APP_API_URL=http://localhost:5000
   ```

4. Start the development server:
   ```bash
   npm start
   ```
   The application will open at `http://localhost:3000`

## Usage

1. **Launch the application**: Ensure both backend and frontend servers are running
2. **Search for reviews**: Use the search bar to find reviews for specific products or topics
3. **View results**: Browse extracted reviews with sentiment analysis and metadata
4. **Filter data**: Use filters for sentiment, date range, or subreddit
5. **Export results**: Download review data in CSV or JSON format

## Configuration

### Reddit API Setup

1. Go to [Reddit's App Preferences](https://www.reddit.com/prefs/apps)
2. Create a new application (select "script")
3. Copy your client ID and secret
4. Add them to your `.env` file in the backend directory

### Backend Configuration

Edit `backend/config.py` to adjust:
- Subreddits to scrape
- Number of posts to retrieve
- Text processing parameters
- Database settings

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/reviews` | GET | Fetch all reviews with optional filters |
| `/api/search` | POST | Search reviews by keyword |
| `/api/reviews/<id>` | GET | Get a specific review |
| `/api/analytics` | GET | Get sentiment analysis and statistics |
| `/api/subreddits` | GET | List tracked subreddits |

## Technologies Used

**Backend:**
- Python 3
- Flask or FastAPI
- PRAW (Python Reddit API Wrapper)
- SQLite/PostgreSQL
- pandas for data processing

**Frontend:**
- TypeScript
- React
- CSS/Tailwind CSS
- Axios for API calls
- Chart.js or similar for data visualization

## Development

### Running Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm test
```

### Code Quality

Ensure code follows project standards:
```bash
# Backend
flake8 backend/src
black backend/src

# Frontend
npm run lint
npm run format
```

## Common Issues

### Reddit API Authentication Fails
- Verify credentials in `.env` file
- Ensure client secret is not exposed in version control
- Check Reddit API rate limits

### CORS Errors
- Configure CORS in backend (`flask-cors` or similar)
- Verify frontend API URL in configuration

### Port Already in Use
- Change the port in `backend/app.py` or `frontend/.env`
- Kill existing processes: `lsof -ti:5000` or `lsof -ti:3000`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes. Ensure you comply with Reddit's Terms of Service and API usage guidelines when scraping data.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation in the project
- Review Reddit API documentation: https://www.reddit.com/dev/api

## Future Enhancements

- Advanced NLP for better sentiment analysis
- Machine learning categorization of reviews
- Real-time data updates with WebSockets
- Export to multiple formats (Excel, PDF)
- User authentication and saved searches
- Mobile application