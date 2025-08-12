# Hi new developer, welcome to Voxify!

<p align="center">
<img src="https://voxify-prod.vercel.app/logo.png" width=50%>
</p>

Voxify is an AI-powered voice cloning and text-to-speech platform that enables users to create personalized synthetic voices from audio samples. The application leverages cutting-edge diffusion transformer technology (F5-TTS) to generate high-quality, natural-sounding speech by capturing tone, rhythm, and accent of different voices.

---

# Overview

Voxify's core capabilities consist of voice sample processing, embedding generation, real-time synthesis, and precise timing control for natural speech patterns.

**Context & Value:** Voice cloning technology addresses the growing demand for personalized audio content across multiple industries. Traditional TTS systems produce generic, robotic voices that lack emotional nuance and personal connection. Voxify solves this by making voice synthesis technology more accessible through a user-friendly API while maintaining enterprise-grade security and performance standards.

The platform's value lies in its ability to capture human vocal identity digitally, thereby enabling content creators, businesses, and individuals to scale personalized audio production without sacrificing authenticity or quality.

---

## Key Use Cases

This project hopes to aid primarily in **content creation and media production**, **business and enterprise applications**, **accessibility and assistive technology**, and **personal and creative applications**. Creators and producers can create high-quality voiceovers, create multiple characters for storytelling, or produce content in their own voice when physically unavailable, all while ensuring consistency in quality. Organizations can enhance their customer experience and streamline communication processes by maintaining consistent service for customer support, marketing messages, or executive communications.

Beyond professional use, Voxify enables personal expression and memory preservation with voice manipulation, character creation, and other settings to preserve loved ones' voices or create fictional voices for creative expression. Additionally, accessibility needs can also be met by providing individuals with speech impairments or language barriers the opportunity to recreate their original voice in speech for their original language or others while preserving vocal identity.

## Key Features

**Voice Cloning and Synthesis:**

- Upload audio samples to create personalized voice models.
- Generate natural-sounding speech from any text input using cloned voices.

**User Management and Security:**

- Secure user authentication and profile management.
- Job status tracking for synthesis requests.

**Technical Infrastructure:**

- RESTful API architecture for easy integration.
- Dual database system and CI/CD pipeline for automated testing and quality assurance.

**AI-Powered Processing:**

- F5-TTS diffusion transformation technology, with fine-tuning options for improved voice quality.
- Model versioning and management capabilities.

---

# Getting Started

**Frontend Production Link:** https://voxify-prod.vercel.app

**Frontend Preview Link:** https://voxify-dev.vercel.app

**Backend Service Link:** https://milaniez-montagy.duckdns.org/

--- 

Here is our landing Page, where users can find related information of our platform:
<p align="center">
  <img src="frontend/src/components/landing.png" width="80%" alt="Voxify landing page">
</p>

Users can create an account and log in. Once they do so, they will be redirected to the user dashboard.

<p align="center">
<img src="https://imgur.com/rkQl6ho.png" width=48% alt= "Voxify registration">
<img src="https://imgur.com/ZubwDd8.png" width=48%alt="Voxify Login">
</p>

The dashboard has access to cloning your voice and the text-to-speech option, as well as statistics of your current voice clones and completed/processed tasks while the audio samples are recording. There is also a set of quick actions where users can view their tasks and profile settings.

<p align="center">
<img src="https://imgur.com/Iczav58.png" width=75% alt="Voxify dashboard" />
</p>

Users can clone their voice using a `.wav` audio sample of their own voice. A 10-second audio file is recommened. Once you name the voice, write a description, and include the reference text of what was said in the audio sample, it will be saved to your account. Users can also record their own voices directly on our website.

<p align="center">
<img src= "frontend/src/components/upload.png"  width=75% alt="Voxify voice generation page1"/>
</p>
<p align="center">
<img src= "frontend/src/components/record.png"  width=75% alt="Voxify voice generation page2"/>
</p>


The text-to-speech page allows users to input any text they want converted to audio using either a voice clone or the system voice(s). The user can also change the language spoken, as well as the speed, pitch, and volume the generated audio output will be when generated.

<p align="center">
<img src="frontend/src/components/task.png" width=75% alt="Voxify TTS page" />
</p>

Generated audio recordings are saved in the "Tasks" tab, and users can then download/play previously generated sound recordings.

<p align="center">
<img src="https://imgur.com/I1BCVjR.png" width=75% alt="Voxify jobs page" />
</p>

<details>
<summary><b>Accessibility Widget (for AI Assignment)</b></summary>
There is an accessibility widget in the bottom right corner that allows users to customize their view to better suit individual needs.

<p align="center">
<img src="https://imgur.com/wdZ0RVf.png" width=75%>
</p>

The customizable options include adhering to accessibility profiles, content adjustments, color adjustments, and orientation adjustments.

<p align="center">
<img src="https://imgur.com/tr49lhN.png" width=24% />
<img src="https://imgur.com/VgC0IXX.png" width=25% />
<img src="https://imgur.com/OqX9m7O.png" width=24% />
<img src="https://imgur.com/hLJhKmo.png" width=24% />
</p>

</details>

---
# API service and fast start locally
Here are some key API endpoints for our backend. For more reference please check backend.ApiDoc.md.
Authentication & Profile
- POST /api/v1/auth/register – Register a new user
- POST /api/v1/auth/login – Log in and receive JWT token
- GET /api/v1/auth/profile – Get current user profile
- PUT /api/v1/auth/profile – Update user profile

Voice Sample Management
- POST /api/v1/voice/samples – Upload a voice sample (WAV/MP3)
- GET /api/v1/voice/samples – List uploaded samples
- DELETE /api/v1/voice/samples/{sample_id} – Delete a sample

Voice Clone Management
- POST /api/v1/voice/clones – Create a voice clone from sample IDs
- GET /api/v1/voice/clones – List voice clones
- POST /api/v1/voice/clones/{clone_id}/synthesize – Synthesize using a clone

Synthesis Job Management
- POST /api/v1/job – Create a new synthesis job
- GET /api/v1/job/{job_id}/progress – Track job progress in real-time
- GET /api/v1/file/synthesis/{job_id} – Download synthesized audio

We have've configured **Swagger** to test our backend locally, pls following these command:
- cd backend
- pip install -r requirements.txt
- python start.py
- Then open http://localhost:8000/docs/

Suggested test flows using Swagger or Postman:

- **Create users**:
Post:/auth/register -> Post:/auth/login -> Set Bear <token> using token returned from previous step

- **Create voice clone**:
Post:/voice/samples -> Post:/voice/clones -> Post:/voice/clones/{clone_id}/select -> Post:/voice/clones/{clone_id}/synthesize

- **Download synthesized audio file**:
Get:/file/synthesis/{job_id}

<img width="870" height="961" alt="image" src="https://github.com/user-attachments/assets/95b0cde8-2aca-4ec6-9eaf-6a1d252a4f93" />

## Backend Structure

Voxify utilises a RESTful API structure. It uses Python and Flask with capabilities for the following:

- User authentication and management
- Voice sample upload and processing
- Voice clone generation and selection
- Text-to-speech synthesis with syllable-to-time or word-to-time mapping
- Synthesis job status monitoring
- Rate limiting and usage tracking

## Frontend Structure

The project uses a React-based frontend with Material UI and Tailwind.
Core Framework:
- React 18.2.0 - Modern React framework using functional components and Hooks
- React Router DOM 6.21.3 - Client-side routing management
- Material UI 5.15.6 - Material Design component library 1
- Tailwind CSS 3.4.1 - Utility-first CSS framework
Additional Dependencies:
- Axios 1.6.7 - HTTP client for API communication
- Emotion - CSS-in-JS solution (Material UI dependency)

## Databases

Voxify uses two databases - a relational database for user management and storage of voice samples, and a vector database for storing voice embeddings.

- SQLite is used to store user profiles, authentication data, and metadata, as well as their uploaded voices.
- ChromaDB is used for storing and querying voice embeddings, each with metadata linking it back to corresponding users or tasks.

## AI Components

The AI functionality of Voxify uses voice synthesis models used for text-to-speech (TTS) generation. We are currently using F5-TTS, which is an open-source TTS synthesis tool using diffusion transformers.

- Voice embeddings are extracted for personalized cloning.
- There will be fine-tuning capabiltiies for improved voice quality.
- Real-time processing is used for immediate feedback.

## Containerization

Docker is used for containerization:

- Docker Compose allows for multiple services to be run and compiled from individual Dockerfiles. A Dockerfile is used across subdirectories for corresponding containers in to be built based on their requirements/dependencies.
- Containers are orchestrated to make local development and testing easy to conduct.
- Integrations with the CI/CD pipeline are integrated for automated builds and testing. Using GitHub Actions, formatting/linting, as well as tests for end-to-end API calls are tested to ensure branch merges do not affect existing test cases and the project is successful.

---

# Deployment

The backend of this project is deployed onto our partner's home computing server that we have privileges to SSH into. It is served via Waitress (WGSI server).
All code is pulled from the GitHub repository, and is built and run using the orchestrated Docker Compose services.

The F5-TTS AI service is also run from the partner's server with a minimum dedicated GPU memory allocation for the service.

The frontend is deployed using Vercel, which takes directly from a GitHub repository. It allows for multiple environments and deployments for preview/development (based on pull requests) and production.

## Running Locally

**Prerequisites:**
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

**Environment Secrets:**

Most of the environment secrets are configured in the `docker-compose.yml` file, however, if required, look at the `.env.example` example below. You will also need a `.env.prod` if trying to deploy to production.

```
DATABASE_URL=sqlite:///data/voxify.db
FRONTEND_URL=localhost:3000
VECTOR_DB_PATH=data/chroma_db
JWT_SECRET_KEY=Majick
SECRET_KEY=Majick
SMTP_FROM_EMAIL=voxifynoreply@gmail.com
SMTP_FROM_NAME=Voxify
SMTP_HOST=smtp.gmail.com
SMTP_PASSWORD=uhxxrskdlliidcyg
SMTP_PORT=587
SMTP_USERNAME=voxifynoreply@gmail.com
SMTP_USE_TLS=true
```

**Local Setup:**

Clone the repository and launch the full stack:
```
git clone https://github.com/csc301-2025-y/project-2-Voxify.git
cd Voxify
make dev
```
Services started:
| Services | Description | URL |
| -------- | ----------- | --- |
| `frontend` | React App (CRA) | http://localhost:3000 |
| `api` | Flask backend API | http://localhost:8000 |
| `db-init` | One-time DB initialization script | N/a|

You can check the backend health using `curl http://localhost:8000/health`.

Additional commands for local testing and deployment can be found using `make help`.

<details>
<summary><i>Click here to see all Makefile targets.</i></summary>
<code>Available targets:
 install         - Install all dependencies
 lint            - Run linting for backend and frontend
 reformat        - Format code for backend and frontend
Testing:
 test            - Run all tests (backend + frontend + security)
 test-backend    - Run only backend tests
 test-frontend   - Run only frontend tests
 test-security   - Run security tests with Snyk
 test-quick      - Run backend tests without full rebuild
Building:
 build           - Build all Docker images
 build-backend   - Build only backend services
 build-frontend  - Build only frontend service
 db-build        - Build database container
Running:
 up              - Start backend services only
 up-full         - Start all services (backend + frontend)
 up-backend      - Alias for 'up' (backend only)
 down            - Stop all services
 frontend        - Start frontend development server locally
Development:
 dev             - Install, lint, build, and start backend services
 logs            - Show logs from running services
 shell           - Open shell in backend container
 clean           - Clean up Docker resources
Production:
 setup-certs     - Setup SSL certificates for Docker
 setup-nginx     - Setup nginx configuration
 prod-build      - Build production images
 prod-up         - Start production services
 prod-down       - Stop production services
 prod-deploy     - Full production setup
 prod-status     - Check production status
 prod-logs       - Show production logs
</code>
</details>

## Testing

Testing is conducted using pytest for the backend using comprehensive fixtures and mocking for the backend.

The frontend uses Jest with React Testing Library for unit and integration testing.

**Running Tests:**

```
make test  # Runs all tests
make test-backend  # Runs only backend tests 
make test-frontend  # Runs only frontend tests
make test-quick  # Runs backend tests without a full rebuild
```

### Backend Testing

Tests are conducted in layers with the following:
- **Unit Tests** - Core logic, utilities, file and audio processing.
- **Service/API Tests** - Full REST API endpoints using Flask test client and `curl`.
- **Integration Tests** - End-to-end workflows across auth, voice, cloning, synthesis, job queues.
- **Performance Tests** - Audio upload, clone generation, TTS response times.
- **Security Tests** - Input validation, path traversal, SQL injecion prevention.

More generally, authentication, voice processing, database, jobs, files, error handling, and external services, were the key areas covered while integrating the project's testing structure.

**Coverage Overview (for D3):**
- **Total Test Cases:** 512
- **Pass Rate:** 96.9% (496 passed, 16 skipped)
- **Coverage:** 85% overall (8985/10,326 lines)
- **High-Coverage Models:** database models, authentication logic, embedding services, error handling
- **Low-Coverage Models:** voice clone APIs, modal integration

**Tools Used:**
- `pytest`
- `pytest-cov` for coverage reporting
- SQLite for isolated test databases
- `psutil` for performance and resource monitoring

### Frontend Testing

Voxify was not initially planned to have a frontend, and tests were not as rigorous as our backend API.

A global test setup is defined in `frontend/src/setupTests.js` to ensure compatability with the React environment. Tests live alongside components using the `.test.js` extension.

For D3, frontend test coverage reached 42% line coverage in 250 tests. For D4, there are plans to achieve at *least* 50% coverage.

**Testing Setup Inclusions:**
- `@testing-library/jest-dom` for extended matchers like `.toBeInTheDocument()`.
- Mocks for browser APIs unavailable in Jest by default:
    - `ResizeObserver`
    - `IntersectionObserver`
    - `matchMedia`
    - `localStorage`
    - `URL.createObjectURL`
    - `HTMLAudioElement`
- Global `fetch` and `alert` mocks.
- Suppressess `console.error` noise during test runs.

### Linting
Linting and formatting checks are done automatically whenever a push is made onto a GitHub branch. The following are checked:
- **Backend** - Black, Flake8
- **Frontend** -  ESLint, Prettier

**Running Lint Checks:**
```
make lint  # For both frontend and backend
make reformat  # Reformats the code for linting
```

## Maintenance

### Dependency Management
Dependencies for the backend are managed in the `requirements.txt` and `requirements-dev.txt`. To update packages:
```
pip list --outdated
pip install --upgrade <package>
```

Frontend dependencies are managed via `npm`. To check and update:
```
npm outdated
npm update
```

Whenever code or dependencies are changed, be sure to end/down all services using `make down` and rebuild using `make build`. 

You can also clear stale volumes or containers using `docker system prune -a --volumes`, but note that this will stop all containers and unused volumes/images.

### Logs and Monitoring

Container logs can be checked using `make logs` and a shell for the backend container is opened through `make shell`. The backend health endpoint is at http://localhost:8000/health.

### Cleanup and Refactoring

Periodically prune unused Docker resources and remove deprecated components and dead code. Also keep documentation and comments up-to-date when updating APIs or architecture.

Dependabot (via GitHub) and linting will typically check for many of these dependency and security-related issues that come with deprecated packages and libraries.

---

# Project Task Management

 **GitHub Projects** and **GitHub Issues** are used to plan, track, and manage our development tasks, and the project boards will serve as the central hub for any work-related activities. 
 
 Progress is checked and tasks are assigned each week during our weekly standups with our partner. Status of the project is also updated regularly and during the sync meetings.

## GitHub Workflow Overview

- **Sprints -** We are operating on a 1-week sprint-based development, where each member is assigned a task to complete for that week. New tasks are added based on our goals and requirements for upcoming milestones, and they may carryover from previous sprints depending on the progress made.
- **Tasks & Issues -** Each task is created as a GitHub issue and is linked to the project board. We assign each task to the member and include the necessary milestones and labels to it. Any development-related tasks also get linked to a new branch beginning with `pr/[ISSUE]`.
- **Labels -** All tasks are labelled based on different types, as a feature, bug, enhcancement, or documentation, as well as a start-to-end date to ensure that all members understand what is being worked on.
- **Project boards -** Columns are divided as "To Do", "In Progress", "Done", where each task gets moved along to reflect current progress. There is also a "Backburner" column for any features that may be considered later on in development but are not a priority.
- **Automation -** GitHub automation is used using CI/CD workflows, ensuring that all issues and pull requests can be synced with the board status and do not have any problems before being pushed to the main branch.

---

# Partner Information:

**Mehdi Zeinali** 

*Engineer of Computer Vision, Network Security and Embedded Solutions*

📧: mehdi@zeina.li  

☎️️: 778-952-3223  


---

# License

**Academic Evaluation License Agreement**

Copyright (c) 2025 Majick

This license governs the use of the software product named "Voxify" (the "Software") developed by Majick and Mehdi Zeinali for academic purposes as part of the CSC301 course.

1. **Grant of License** -
You are hereby granted a limited, non-exclusive, non-transferable, revocable license to use the Software solely for the purpose of academic evaluation and coursework related to CSC301.

2. **Restrictions** -
You may not: 
(a) Use the Software for any commercial purpose; 
(b) Modify, reverse engineer, decompile, disassemble, or create derivative works based on the Software; 
(c) Distribute, sublicense, rent, lease, or transfer the Software or any portion thereof to any third party; 
(d) Use the Software beyond the scope of CSC301 coursework without prior written permission from the Majick team.

3. **Ownership** -
All intellectual property rights in and to the Software remain the sole property of Maijck. This license does not convey any ownership rights to you.

4. **Term** -
This license is effective from the date of access and shall automatically terminate upon conclusion of the CSC301 course, or earlier if you fail to comply with any of the terms. Upon termination, you must cease all use of the Software and destroy any copies in your possession.

5. **Disclaimer of Warranty** -
The Software is provided "as is" without warranty of any kind, express or implied. Majick will make no warranties, including but not limited to the implied warranties of merchantability or fitness for a particular purpose.

6. **Limitation of Liability** -
In no event shall Majick be liable for any damages arising from the use or inability to use the Software, including but not limited to incidental, consequential, or special damages.

By using the Software, you agree to the terms of this license.
