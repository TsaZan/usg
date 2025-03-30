# UGC Automation Platform

An AI-driven Django application that automates the discovery, analysis, and management of user-generated content from social media platforms. It integrates seamlessly with Instagram, TikTok, and Facebook APIs to enhance brand engagement through intelligent content curation.

## Features

- **AI-Powered Content Detection:** Automatically identifies and classifies relevant UGC across multiple social media channels.
- **Content Analysis:** Evaluates engagement metrics and authenticity to prioritize high-quality content.
- **Marketing Recommendations:** Provides actionable insights for content sharing and remixing strategies.
- **Multi-Platform Integration:** Ensures smooth connectivity with Instagram, TikTok, and Facebook for comprehensive content management.
- **Automated Responses:** Utilizes AI to generate personalized captions and replies to user interactions.

## Technologies Used

- **Backend:** Python 3.8+, Django 4.2.7, Django REST Framework 3.14.0
- **Task Queue:** Celery, Redis
- **Database:** PostgreSQL
- **AI/ML Services:** OpenAI API, Google Vision AI
- **APIs:** Instagram Graph API, TikTok API, Facebook Graph API

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher
- Git

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/TsaZan/usg.git
   cd usg
   ```

2. **Create and Activate Virtual Environment:**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On Unix or MacOS
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**
   - Copy `.env.example` to `.env`
   - Update the variables in `.env` with your configuration

5. **Set Up Database:**
   ```bash
   # Create PostgreSQL database
   createdb ugc_platform
   
   # Run migrations
   python manage.py migrate
   ```

6. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server:**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
usg/
├── ugc_platform/          # Main project directory
├── ugc_users/            # User management app
├── ugc_content/          # Content management app
├── ugc_social/           # Social media integration app
├── ugc_ai/               # AI/ML services app
├── ugc_analytics/        # Analytics and reporting app
├── ugc_api/              # API endpoints app
├── templates/            # HTML templates
├── static/              # Static files
├── media/               # User-uploaded files
└── manage.py            # Django management script
```

## Development

- **Code Style:** Follow PEP 8 and use Black for formatting
- **Testing:** Use pytest for running tests
- **Linting:** Use flake8 for code linting

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

