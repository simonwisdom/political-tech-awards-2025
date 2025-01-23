# Political Technology Awards Allocation System

A Streamlit application for allocating a £5M budget across 293 political technology projects, with multi-user support and data persistence.

## Features

- Multi-user support with email verification
- Real-time budget allocation and validation
- Project filtering and search functionality
- Analytics dashboard with visualizations
- Data export capabilities
- Concurrent allocation management

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Prepare the data:
- Place your projects data in `data/projects.csv` with the following columns:
  - project_id
  - name
  - description
  - category
  - status

4. Run the application:
```bash
streamlit run main.py
```

## Usage

1. **Authentication**:
   - Enter your email address
   - Click "Start Verification"
   - Check your email for the verification link (development mode shows link in sidebar)
   - Click the link to verify your email

2. **Project Explorer**:
   - Browse all projects
   - Use filters and search to find specific projects
   - View project details and allocate funding

3. **Budget Allocation**:
   - Enter allocation amounts for projects
   - Stay within the £5M total budget
   - Allocations are saved automatically

4. **Analysis Dashboard**:
   - View allocation metrics
   - See category breakdowns
   - Export allocation data

## Development

- The application uses SQLite for data persistence
- Session state manages user authentication
- Real-time validation ensures budget constraints
- Concurrent access is handled via connection pooling

## Security

- Email verification required for access
- Rate limiting on verification attempts
- Input validation and sanitization
- SQL injection prevention
- Token-based authentication

## File Structure

```
app/
├── main.py          # Streamlit interface and routing
├── database.py      # SQLite operations and models
├── auth.py          # Email verification system
├── utils.py         # Helper functions and validators
├── config.py        # Configuration and constants
└── data/
    ├── db.sqlite3   # SQLite database
    └── projects.csv # Project data source
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 