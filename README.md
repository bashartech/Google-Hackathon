# ServiceLink AI - Home Service Booking Platform

![Status](https://img.shields.io/badge/status-ready-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Next.js](https://img.shields.io/badge/next.js-14.0-black)
![License](https://img.shields.io/badge/license-MIT-blue)

> **Multi-Agent AI System for Informal Economy Service Orchestration**  
> Built for Antigravity Hackathon - Challenge 2: AI Service Orchestrator for Informal Economy

---

## 🎯 Project Overview

ServiceLink AI is an intelligent home service booking platform that connects customers with informal service providers in Islamabad, Pakistan. The system uses **5 specialized AI agents** powered by OpenAI Agents SDK and Groq API to orchestrate the entire booking workflow from request to confirmation.

### Key Features

- 🌍 **Multi-Language Support** - Understands Urdu, Roman Urdu, and English
- 📍 **Real Location Services** - Google Maps API for accurate distance calculation
- 🤖 **5-Agent Orchestration** - Specialized agents for each workflow stage
- ⭐ **Intelligent Matching** - Ranks providers by distance, rating, response time, experience
- 📧 **Email Notifications** - Automated booking confirmations and follow-ups
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile
- 🚨 **Urgency Detection** - Emergency, high priority, and normal request handling

---

## 🏗️ Architecture

### Multi-Agent System

```
Customer Request (Urdu/Roman Urdu/English)
    ↓
┌─────────────────────────────────────────┐
│   Service Request Coordinator           │
│   • Detects language                    │
│   • Translates to English               │
│   • Extracts service type & location    │
│   • Determines urgency level            │
└─────────────────┬───────────────────────┘
                  ↓ handoff
┌─────────────────────────────────────────┐
│   Provider Discovery Agent              │
│   • Searches by service type            │
│   • Uses Google Maps for distance       │
│   • Filters by rating & availability    │
│   • Returns qualified providers         │
└─────────────────┬───────────────────────┘
                  ↓ handoff
┌─────────────────────────────────────────┐
│   Matching & Ranking Agent              │
│   • Calculates ranking scores           │
│   • Applies urgency-based weights       │
│   • Selects top 3 recommendations       │
│   • Provides reasoning                  │
└─────────────────┬───────────────────────┘
                  ↓ handoff
┌─────────────────────────────────────────┐
│   Booking & Confirmation Agent          │
│   • Creates booking record              │
│   • Generates booking ID                │
│   • Sends email notifications           │
│   • Returns booking summary             │
└─────────────────┬───────────────────────┘
                  ↓ handoff
┌─────────────────────────────────────────┐
│   Follow-up Agent                       │
│   • Sends reminder emails               │
│   • Collects feedback                   │
│   • Handles rescheduling                │
│   • Processes cancellations             │
└─────────────────────────────────────────┘
```

### Tech Stack

**Backend:**
- **Framework:** FastAPI (Python)
- **AI Orchestration:** OpenAI Agents SDK
- **LLM:** Groq API (Llama 3.3 70B)
- **Location:** Google Maps API (Geocoding + Distance Matrix)
- **Translation:** Deep Translator + LangDetect
- **Email:** Gmail SMTP
- **Database:** JSON (mock data for hackathon)

**Frontend:**
- **Framework:** Next.js 14 (React 18)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Responsive:** Mobile-first design

---

## 📋 Available Services

1. **❄️ AC Repair** - Installation, repair, maintenance, gas refilling
2. **🔧 Plumbing** - Pipe repair, drain cleaning, water tank installation
3. **⚡ Electrician** - Wiring, circuit repair, fan/light installation
4. **🧹 Home Cleaning** - Deep cleaning, regular cleaning, kitchen/bathroom
5. **🪚 Carpenter** - Furniture repair, door installation, cabinet making
6. **🎨 Painter** - Interior/exterior painting, wall texture, waterproofing

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API Key ([Get here](https://console.groq.com))
- Google Maps API Key ([Get here](https://console.cloud.google.com))
- Gmail account (for email notifications)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit backend/.env and add:
# GROQ_API_KEY=your_groq_api_key_here
# GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
# EMAIL_USER=your_gmail@gmail.com
# EMAIL_PASSWORD=your_gmail_app_password

# Start backend server
python main.py
```

Backend runs on: **http://localhost:8001**

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: **http://localhost:3000**

### 3. Test the System

Open **http://localhost:3000** and try these multi-language requests:

**English:**
```
I need an AC repair service in G-13
```

**Roman Urdu:**
```
Mujhe plumber chahiye F-10 mein, urgent hai
```

**Urdu:**
```
مجھے الیکٹریشن چاہیے بلیو ایریا میں
```

**Emergency:**
```
EMERGENCY: AC not working, need immediate repair in G-11
```

---

## 🧪 Testing Examples

### Example 1: Basic Service Request
```
Input: "I need AC repair in G-13"

Expected Output:
✅ Language detected: English
✅ Service type: AC Repair
✅ Location: G-13, Islamabad
✅ Providers found: 1 (Ali AC Services)
✅ Distance: 2.5 km
✅ Booking confirmed: BKG0001
```

### Example 2: Roman Urdu with Urgency
```
Input: "Mujhe plumber chahiye F-10 mein, jaldi hai"

Expected Output:
✅ Language detected: Roman Urdu
✅ Translated: "I need plumber in F-10, quickly"
✅ Service type: Plumbing
✅ Urgency: HIGH
✅ Provider: Hassan Plumbing Services
✅ Response time: 30 minutes
```

### Example 3: Emergency Request
```
Input: "EMERGENCY: Bijli ka masla hai I-8 mein"

Expected Output:
✅ Language detected: Roman Urdu
✅ Service type: Electrician
✅ Urgency: EMERGENCY
✅ Provider: Sarah Electricals (closest + fastest response)
✅ Distance: 1.8 km
✅ Response time: 40 minutes
```

---

## 📊 Sample Provider Data

The system includes **6 fictional service providers** with **real Islamabad addresses**:

| Provider | Service | Location | Rating | Experience |
|----------|---------|----------|--------|------------|
| Ali AC Services | AC Repair | G-13/1 | 4.8★ | 8 years |
| Hassan Plumbing | Plumbing | F-10 Markaz | 4.6★ | 6 years |
| Sarah Electricals | Electrician | I-8/3 | 4.9★ | 10 years |
| Zainab Home Cleaning | Cleaning | G-11/2 | 4.7★ | 5 years |
| Ahmed Carpentry | Carpenter | F-7 Kohsar | 4.5★ | 12 years |
| Bilal Painting | Painter | G-10/4 | 4.4★ | 7 years |

All addresses are **geocoded using Google Maps API** for accurate distance calculations.

---

## 🤖 Agent Details

### 1. Service Request Coordinator
- **Role:** Multi-language request understanding
- **Tools:** LangDetect, Deep Translator, NLP extraction
- **Input:** Natural language in Urdu/Roman Urdu/English
- **Output:** Structured service request data
- **Handoff:** → Provider Discovery Agent

### 2. Provider Discovery Agent
- **Role:** Find available service providers
- **Tools:** Database search, Google Maps Geocoding
- **Input:** Service type, location, urgency
- **Output:** List of qualified providers with distances
- **Handoff:** → Matching & Ranking Agent

### 3. Matching & Ranking Agent
- **Role:** Intelligent provider ranking
- **Tools:** Multi-factor scoring algorithm
- **Ranking Factors:**
  - **Emergency:** Distance (35%) + Response Time (40%) + Rating (20%) + Experience (5%)
  - **High:** Distance (30%) + Rating (35%) + Response Time (25%) + Experience (10%)
  - **Normal:** Rating (40%) + Experience (20%) + Distance (25%) + Response Time (15%)
- **Output:** Top 3 ranked providers with reasoning
- **Handoff:** → Booking & Confirmation Agent

### 4. Booking & Confirmation Agent
- **Role:** Create booking and send notifications
- **Tools:** Database manager, Email service
- **Actions:**
  - Generate unique booking ID (BKG0001, BKG0002, etc.)
  - Save booking to database
  - Send confirmation email to customer
  - Send notification email to provider
- **Output:** Booking confirmation with provider details
- **Handoff:** → Follow-up Agent

### 5. Follow-up Agent
- **Role:** Post-booking communication
- **Tools:** Email scheduler, Feedback collector
- **Actions:**
  - Send reminder 24 hours before service
  - Collect feedback after completion
  - Handle rescheduling requests
  - Process cancellations
- **Output:** Follow-up status and feedback

---

## 📡 API Endpoints

### Service Booking

**POST** `/api/service-request`
```json
{
  "message": "I need AC repair in G-13"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Booking Confirmed!\n\nBooking ID: BKG0001\nService: AC Repair\nProvider: Ali AC Services\nDistance: 2.5 km away\nRating: 4.8 stars\n...",
  "timestamp": "2026-05-15T10:30:00"
}
```

### Get Booking Status

**GET** `/api/bookings/{booking_id}`

**Response:**
```json
{
  "status": "success",
  "booking": {
    "booking_id": "BKG0001",
    "service_type": "AC Repair",
    "provider_name": "Ali AC Services",
    "status": "confirmed",
    "date": "2026-05-16",
    "time": "10:00 AM"
  }
}
```

### Cancel Booking

**DELETE** `/api/bookings/{booking_id}?reason=Customer request`

### Get Providers

**GET** `/api/providers?service_type=AC Repair&area=G-13`

### Get All Service Types

**GET** `/api/service-types`

**Response:**
```json
{
  "service_types": [
    "AC Repair",
    "Plumbing",
    "Electrician",
    "Home Cleaning",
    "Carpenter",
    "Painter"
  ],
  "service_categories": [
    "Home Appliances",
    "Home Maintenance",
    "Cleaning Services"
  ]
}
```

---

## 🗂️ Project Structure

```
ServiceLink-AI/
├── backend/
│   ├── config/
│   │   └── settings.py              # Configuration with Google Maps
│   ├── database/
│   │   ├── db_manager.py            # Database operations
│   │   ├── service_providers.json   # 6 providers with real addresses
│   │   └── bookings.json            # Booking records
│   ├── scheduling_agents/
│   │   └── service_orchestrator.py  # 5-agent orchestration
│   ├── utils/
│   │   ├── location_service.py      # Google Maps integration
│   │   ├── language_processor.py    # Multi-language NLP
│   │   └── matching_engine.py       # Provider ranking logic
│   ├── tools/
│   │   └── email_tools.py           # Email notifications
│   ├── main.py                      # FastAPI application
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # ServiceLink AI main page
│   │   ├── layout.tsx               # Root layout
│   │   └── globals.css              # Global styles
│   ├── components/
│   │   ├── ChatWindow.tsx           # Chat interface
│   │   ├── WorkflowTimeline.tsx     # Agent workflow display
│   │   └── AgentReasoning.tsx       # AI reasoning display
│   ├── lib/
│   │   └── api.ts                   # API client
│   └── package.json
│
└── README.md
```

---

## 🔑 Environment Variables

### Backend (.env)

```env
# Required
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Email Configuration (Required for notifications)
EMAIL_USER=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

# SMTP Settings
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=465

# Groq Model Configuration
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=2048

# Application Settings
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

---

## 🎯 Hackathon Alignment

### Challenge 2: AI Service Orchestrator for Informal Economy

✅ **Multi-Agent Orchestration** - 5 specialized agents working together  
✅ **Intent Understanding** - NLP for Urdu, Roman Urdu, English  
✅ **Provider Matching** - Google Maps-based location matching  
✅ **Decision Making** - Intelligent ranking algorithm with urgency handling  
✅ **Action Execution** - Automated booking and email notifications  
✅ **Workflow Transparency** - Clear agent reasoning and workflow display  

### Innovation Points

1. **🌍 Multi-Language NLP** - Supports Pakistan's linguistic diversity (Urdu, Roman Urdu, English)
2. **📍 Real Location Services** - Google Maps integration (no dummy/fallback data)
3. **🚨 Urgency-Based Ranking** - Different algorithms for emergency vs normal requests
4. **🏠 Informal Economy Focus** - Targets home service providers in Pakistan
5. **⚡ End-to-End Automation** - From request to confirmation in seconds
6. **📧 Email Integration** - Real email notifications for bookings and follow-ups

---

## 🌟 Key Features Demonstration

### 1. Multi-Language Understanding
```
Input (Urdu): "مجھے اے سی ریپیئر چاہیے"
→ Detected: Urdu
→ Translated: "I need AC repair"
→ Service: AC Repair
```

### 2. Location-Based Matching
```
Customer Location: G-13, Islamabad
→ Google Maps Geocoding: 33.6844° N, 73.0479° E
→ Provider Location: G-13/1, Islamabad
→ Distance Calculation: 2.5 km (Haversine formula)
→ Travel Time: ~8 minutes
```

### 3. Intelligent Ranking
```
Emergency Request:
→ Provider A: Distance 2km, Rating 4.5, Response 60min → Score: 78
→ Provider B: Distance 5km, Rating 4.9, Response 30min → Score: 85 ✅
→ Selected: Provider B (faster response prioritized)
```

---

## 🚀 Future Enhancements (Post-Hackathon)

- [ ] Google Calendar integration for scheduling
- [ ] User authentication and profiles
- [ ] Payment gateway integration (JazzCash, EasyPaisa)
- [ ] Provider mobile app
- [ ] Real-time GPS tracking
- [ ] Rating and review system
- [ ] WhatsApp integration for notifications
- [ ] Voice input support (Urdu speech recognition)
- [ ] Deployment to Google Cloud / Digital Ocean
- [ ] PostgreSQL database migration
- [ ] Provider verification system
- [ ] Service history and analytics

---

## 🔒 Security & Privacy

- ✅ No hardcoded API keys in code
- ✅ Environment variables for sensitive data
- ✅ Input validation on all endpoints
- ✅ Secure email transmission (SSL/TLS)
- ✅ Customer data privacy maintained
- ✅ Provider information protected

---

## 📄 License

MIT License - Built for Antigravity Hackathon 2026

---

## 🙏 Acknowledgments

- **OpenAI Agents SDK** - Multi-agent orchestration framework
- **Groq** - Fast LLM inference with Llama 3.3 70B
- **Google Maps** - Location services and geocoding
- **Antigravity** - Hackathon platform and IDE
- **Deep Translator** - Multi-language translation
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework for production

---

## 📞 Support

For questions or issues:
1. Check backend logs: `backend/main.py` console output
2. Verify environment variables in `backend/.env`
3. Ensure Google Maps API key has Geocoding + Distance Matrix enabled
4. Test API endpoints at: http://localhost:8001/docs

---

## ⭐ Show Your Support

If you found this project helpful, please give it a star! ⭐

---

**Built with ❤️ using Antigravity IDE**

*ServiceLink AI - Connecting Pakistan's informal economy with AI-powered service orchestration*
