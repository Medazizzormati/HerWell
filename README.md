# HERwell AI

A supportive AI companion for women students and graduates in Tunisia. Non-diagnostic wellbeing and study support with a professional, elegant design.

## 🌟 Features

- **Mood Check-ins**: Track your wellbeing with private, optional check-ins
- **AI Assistant**: 3D avatar with voice interaction and text chat
- **Study Planner**: Deterministic scheduling to make exam prep manageable
- **Technical PFE Assistant**: AI-powered engineering copilot for debugging and project development
- **Women's Wellbeing**: Privacy-first menstrual health tracking with educational resources
- **Breathing Exercises**: Guided relaxation techniques
- **Resource Library**: Educational materials on stress, sleep, and study habits

## 🎨 Design

- **Primary Color**: #652D90 (Elegant Purple)
- **Typography**: Cormorant Garamond (headings) + Jost (body)
- **Animations**: Smooth scroll reveals and page transitions

## 🏗️ Tech Stack

### Frontend
- React 18 with Vite
- Three.js for 3D avatar
- Recharts for data visualization
- Lucide React for icons

### Backend
- Spring Boot 3.2.0
- Spring Security
- Spring Data JPA
- H2 Database (in-memory)
- Maven

## 🚀 Quick Start

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on http://localhost:5173

### Backend
```bash
cd springboot-backend
mvn spring-boot:run
```
Backend runs on http://localhost:8080

### H2 Console
Access H2 console at http://localhost:8080/h2-console
- JDBC URL: `jdbc:h2:mem:herwelldb`
- Username: `sa`
- Password: (empty)

## 📱 Pages

- **Dashboard** - Overview of your wellbeing space
- **Mood Check-in** - Track your mood, stress, and energy
- **AI Assistant** - 3D avatar with voice and text chat
- **Technical PFE** - AI-powered technical assistance
- **Women's Wellbeing** - Privacy-first menstrual health tracking
- **Study Planner** - Manage your study tasks and time
- **Resources** - Educational materials and tips
- **Breathing** - Guided breathing exercises
- **Settings** - App preferences
- **Support** - Help and support resources
- **Privacy** - Data handling and safety information

## 🔒 Privacy & Safety

- **Not a medical service**: HERwell AI provides educational support only
- **No diagnosis**: Does not diagnose conditions or replace professional care
- **Privacy-first**: Women's Wellbeing data requires explicit consent
- **Demo mode**: This prototype uses demo data only
- **Local storage**: Data stored in in-memory database for demo

## 📄 License

This project is for the HERwin Hackathon organized by IEEE Women in Engineering at École Polytechnique de Sousse, Tunisia.

## 👥 Authors

- HERwell AI Team
- IEEE Women in Engineering - École Polytechnique de Sousse

## 🙏 Acknowledgments

- FastAPI (original backend)
- Spring Boot (current backend)
- React & Vite (frontend framework)
