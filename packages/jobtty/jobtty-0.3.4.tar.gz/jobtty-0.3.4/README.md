# 🚀 Jobtty.io - Terminal Job Board

Find your next role from the command line! A beautiful, interactive terminal interface for job searching across multiple platforms.

```
     ██╗ ██████╗ ██████╗ ████████╗████████╗██╗   ██╗
     ██║██╔═══██╗██╔══██╗╚══██╔══╝╚══██╔══╝╚██╗ ██╔╝
     ██║██║   ██║██████╔╝   ██║      ██║    ╚████╔╝ 
██   ██║██║   ██║██╔══██╗   ██║      ██║     ╚██╔╝  
╚█████╔╝╚██████╔╝██████╔╝   ██║      ██║      ██║   
 ╚════╝  ╚═════╝ ╚═════╝    ╚═╝      ╚═╝      ╚═╝   
                                                     
    🚀 Terminal Job Board • Find your next role
```

## Features

- 🔍 **Multi-platform Search**: Search jobs across ThamesAI.co.uk, Flutter.pl, and FlutterLondon.com
- 💳 **Premium Features**: Stripe-powered premium job postings and featured listings
- 🎨 **Beautiful Terminal UI**: Rich colors, ASCII art, and interactive menus
- 🔐 **Secure Authentication**: Keyring-based secure token storage
- 📊 **Analytics**: Track your applications and job posting performance
- 🔖 **Bookmarking**: Save jobs for later review
- ⚙️ **Configurable**: Customize location, currency, and search preferences

## Installation

```bash
pip install jobtty
```

Or install from source:
```bash
git clone https://github.com/croscomsoftware/jobtty.git
cd jobtty
pip install -e .
```

## Quick Start

```bash
# Interactive mode
jobtty

# Search for jobs
jobtty search "python developer"
jobtty search "flutter" --remote --salary 80k

# Authentication
jobtty login
jobtty whoami

# Job posting
jobtty post --interactive

# Premium features
jobtty buy premium-listing --duration 30d
```

## Commands

### Authentication
```bash
jobtty login                    # Login to job board services
jobtty logout                   # Logout from all services
jobtty whoami                   # Show current user info
```

### Job Search
```bash
jobtty search "query"           # Search all job boards
jobtty search --remote          # Remote jobs only
jobtty search --location "City" # Location filter
jobtty search --salary 80k      # Minimum salary filter
jobtty show 42                  # Show job details
jobtty save 42                  # Bookmark job
jobtty list --saved             # Show saved jobs
```

### Job Posting
```bash
jobtty post                     # Interactive job posting
jobtty post --title "Developer" --company "TechCorp"
jobtty my-posts                 # Show your job postings
```

### Premium Features
```bash
jobtty buy                      # Browse premium catalog
jobtty buy premium-listing      # Upgrade to premium
jobtty buy featured-post --job-id 123
jobtty billing --history       # Payment history
```

### Configuration
```bash
jobtty config --location "Warsaw"
jobtty config --currency "EUR"
jobtty config --show           # Show all settings
```

## API Integration

Jobtty integrates with:

- **Jobtty.io Production API**: Main job board with 50+ companies (Meta, Google, Apple, Microsoft, Amazon, Spotify, etc.)
- **ThamesAI.co.uk**: AI and technology jobs in London
- **Flutter.pl**: Flutter and mobile development jobs in Poland  
- **FlutterLondon.com**: Flutter community jobs in London

### Real-time Notifications

Get job alerts directly in your terminal while coding:

```bash
# Start the notification daemon
jobtty daemon start

# Continue coding... 
# 🎯 NEW JOB MATCH! (94% match)
# 🏢 Google - Senior React Developer
# 📍 London 🏠 Remote | 💰 £90K-120K
# 🚀 jobtty apply ext_001
```

## Premium Features

### 💎 Premium Listings (£29/month)
- Featured placement in search results
- 3x more visibility
- Priority positioning
- Advanced analytics

### 🚀 Featured Posts (£49/month)
- Top of search results
- Highlighted appearance
- Social media promotion
- Extended duration (45 days)

### 📊 Analytics Pro (£19/month)
- Detailed application metrics
- Candidate source tracking
- Performance benchmarking
- Export capabilities

### 🎨 Company Branding (£99/month)
- Custom brand colors
- Company logo integration
- Branded company page
- Custom email templates

## Configuration

Jobtty stores configuration in `~/.jobtty/`:
- `config.json`: User preferences and settings
- `user.json`: Current user information
- Secure tokens stored in system keyring

Default configuration:
```json
{
  "location": "London, UK",
  "currency": "GBP", 
  "remote_only": false,
  "salary_min": 0,
  "preferred_sources": ["thamesai", "flutter_pl", "flutter_london"],
  "display_mode": "table",
  "auto_save_searches": true,
  "theme": "cyber"
}
```

## Development

```bash
# Setup development environment
git clone https://github.com/croscomsoftware/jobtty.git
cd jobtty
pip install -e .
pip install -r requirements-dev.txt

# Run tests
pytest

# Run CLI in development
python -m jobtty.cli
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- 🌐 Website: https://jobtty.io
- 📧 Email: support@jobtty.io
- 🐛 Issues: https://github.com/croscomsoftware/jobtty/issues

---

Made with ❤️ by [Croscom Software](https://croscomsoftware.com)