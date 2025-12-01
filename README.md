<div align="center">
    <!-- <img src="frontend/public/apple-touch-icon.png" alt="AURALIS Logo" width="100" height="100"> -->
    <h1>AURALIS</h1>
    <p><em>The FIRST EVER Personalized AI Doctor</em></p>
</div>

---

## Overview

**AURALIS** is the first-ever avatar-based AI-powered virtual doctor that combines cutting-edge artificial intelligence, real-time emotion detection, and immersive 3D avatars to deliver personalized medical consultations. By analyzing facial expressions and adapting responses based on emotional states, AURALIS provides empathetic, context-aware healthcare guidance that feels truly human. View this project on the [website](https://stop-googling-symptoms.tech/) or on [Devpost](https://devpost.com/software/docai-evq74t)


---
## Demo Images
<div style="display: flex; flex-wrap: wrap; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/011d3388-540d-401c-a130-58c9c32a14c5" alt="Screenshot 1" width="48%" />
  <img src="https://github.com/user-attachments/assets/1ecea655-e524-48e5-adad-6275a9fdfcbd" alt="Screenshot 2" width="48%" />
  <img src="https://github.com/user-attachments/assets/789bb60d-b837-4214-99c0-67473e90312f" alt="Screenshot 3" width="48%" />
  <img src="https://github.com/user-attachments/assets/7854c67c-5c99-43a7-ad7a-7a684f120476" alt="Screenshot 4" width="48%" />
</div>

---

## How AURALIS Works

### 1. **Landing & Setup**
- Users are greeted with an elegant landing page featuring a dynamic liquid ether background
- Customize your consultation experience by selecting avatar appearance, voice type, and background settings

### 2. **Real-Time Video Consultation**
- **3D Avatar Doctor**: Interact with a lifelike, lip-synced 3D doctor avatar powered by Three.js
- **Webcam Integration**: Your webcam captures your facial expressions in real-time
- **Emotion Detection**: Advanced face-api.js analyzes your emotions (happy, sad, anxious, neutral, etc.)
- **Voice Conversation**: Speak naturally with the AI doctor using ElevenLabs speech-to-text and text-to-speech
- **Intelligent Responses**: Google Gemini AI processes your concerns and adapts its tone based on detected emotions
- **Live Transcript**: View the conversation in real-time with a scrolling chat display

### 3. **Emotion-Aware AI**
The backend continuously monitors:
- **Facial Emotions**: Detected from your webcam feed
- **Sentiment Analysis**: Extracted from your spoken words
- **Emotion Mismatch Detection**: Identifies when your words don't match your facial expressions (e.g., saying "I'm fine" while looking distressed)
- **Adaptive Communication**: The AI adjusts its empathy level, reassurance, and medical guidance based on your emotional state

### 4. **Post-Consultation Summary**
- **Insights Dashboard**: Visual timeline of your emotions throughout the consultation
- **Key Concerns**: AI-extracted summary of your main health issues
- **Recommendations**: Personalized next steps and medical advice
- **Professional PDF Report**: Download a formal medical report signed by "AURALIS AI System"

---

## Tech Stack

### **Frontend**
| Technology | Purpose |
|------------|---------|
| **Next.js 16** | React framework for server-side rendering and routing |
| **React 19** | UI component library |
| **TypeScript** | Type-safe JavaScript |
| **Tailwind CSS 4** | Utility-first CSS framework for styling |
| **Three.js** | 3D avatar rendering and animations |
| **Framer Motion** | Smooth animations and transitions |
| **face-api.js** | Real-time facial emotion detection |
| **jsPDF** | Professional PDF report generation |
| **ReactBits** | Custom UI components (LiquidEther background) |

### **Backend**
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python web framework |
| **Uvicorn** | ASGI server for FastAPI |
| **Google Gemini AI** | Large language model for medical consultations |
| **ElevenLabs** | Text-to-speech (TTS) and speech-to-text (STT) |
| **face-api.js** | Emotion detection from webcam feed |
| **VADER Sentiment** | Sentiment analysis for emotion mismatch detection |
| **Pydantic** | Data validation and settings management |
| **python-dotenv** | Environment variable management |

### **APIs & Services**
- **Google Gemini API**: Powers the conversational AI doctor
- **ElevenLabs API**: Provides natural voice synthesis and speech recognition
- **WebRTC**: Real-time audio/video streaming

---

## Getting Started

### **Prerequisites**
- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **npm** or **yarn**
- **pip** (Python package manager)

### **Environment Variables**

#### Backend (.env)
Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_google_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

#### Frontend (.env.local)
Create a `.env.local` file in the `frontend/` directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Installation & Setup

### **Backend Setup**

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

---

### **Frontend Setup**

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

---

## Usage

1. **Start both servers** (backend on port 8000, frontend on port 3000)
2. **Open your browser** and navigate to `http://localhost:3000`
3. **Click "Get Started"** on the landing page
4. **Customize your experience** (avatar, voice, background)
5. **Allow webcam and microphone access** when prompted
6. **Start your consultation** by speaking naturally to the AI doctor
7. **End the call** when finished to view your summary and download the PDF report

---

## Project Structure

```
hackwestern/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── routers/                # API route handlers
│   │   ├── conversation.py     # Gemini AI conversation endpoint
│   │   ├── tts.py              # ElevenLabs TTS/STT endpoints
│   │   └── insights.py         # Emotion analysis endpoints
│   ├── services/               # Business logic
│   │   ├── gemini_service.py   # Gemini AI integration
│   │   ├── elevenlabs_service.py # ElevenLabs integration
│   │   └── emotion_analyzer.py # Emotion detection & analysis
│   └── models/                 # Pydantic data models
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main application entry
│   │   ├── layout.tsx          # Root layout
│   │   ├── globals.css         # Global styles
│   │   ├── components/         # React components
│   │   │   ├── LandingPage.tsx
│   │   │   ├── SetupPage.tsx
│   │   │   ├── CallInterface.tsx
│   │   │   ├── Avatar.tsx      # 3D avatar component
│   │   │   ├── VideoFeed.tsx   # Webcam + emotion detection
│   │   │   ├── AudioController.tsx # Voice interaction
│   │   │   ├── ChatDisplay.tsx
│   │   │   ├── SummaryPage.tsx
│   │   │   ├── InsightsDashboard.tsx
│   │   │   └── LiquidEther.tsx # Animated background
│   │   └── utils/
│   │       └── pdfGenerator.ts # PDF report generation
│   ├── package.json            # Node dependencies
│   └── tailwind.config.ts      # Tailwind configuration
│
└── README.md
```

---

## Key Features

### **Emotion Detection Pipeline**
1. Webcam captures user's face at 30 FPS
2. face-api.js detects facial landmarks and expressions
3. Emotions are classified (happy, sad, angry, fearful, disgusted, surprised, neutral)
4. Backend receives emotion data and analyzes patterns
5. Gemini AI adjusts responses based on emotional context

### **Voice Interaction Flow**
1. User speaks → Browser captures audio
2. Audio sent to ElevenLabs STT → Transcribed to text
3. Text + emotion data sent to Gemini AI
4. Gemini generates empathetic response
5. Response sent to ElevenLabs TTS → Audio generated
6. Avatar lip-syncs to audio playback

### **Adaptive AI Behavior**
- **High Anxiety Detected**: More reassuring, slower-paced responses
- **Sadness Detected**: Increased empathy and validation
- **Emotion Mismatch**: AI probes deeper ("You say you're fine, but you seem worried...")
- **Neutral/Happy**: Standard medical consultation tone

---

## Privacy & Disclaimers

- All webcam and audio data is processed in real-time and **not stored**
- Conversations are **not saved** after the session ends
- AURALIS is an **AI assistant** and does not replace professional medical advice
- Always consult a licensed healthcare provider for serious medical concerns

---

## Team

Built with ❤️ at Hack Western by 

---

<div align="center">
    <p><strong>AURALIS</strong> - Kickstarting the Future of Healthcare</p>
</div>
