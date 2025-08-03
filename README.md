# Voxify

<p align="center">
<img src="https://voxify-prod.vercel.app/logo.png" width=50%>
</p>

Voxify is an AI-powered voice cloning and text-to-speech platform that enables users to create personalized synthetic voices from audio samples. The application leverages cutting-edge diffusion transformer technology (F5-TTS) to generate high-quality, natural-sounding speech that mimics individual voice characteristics.

---

# Overview

Voxify's core capabilities consist of voice sample processing, embedding generation, real-time synthesis, and precise timing control for natural speech patterns.

**Context & Value:** Voice cloning technology addresses the growing demand for personalized audio content across multiple industries. Traditional TTS systems produce generic, robotic voices that lack emotional nuance and personal connection. Voxify solves this by democratizing voice synthesis technology, making it accessible through a user-friendly API while maintaining enterprise-grade security and performance standards.

The platform's value lies in its ability to preserve human vocal identity digitally, enabling content creators, businesses, and individuals to scale personalized audio production without sacrificing authenticity or quality.

---

## Key Use Cases

This project hopes to aid primarily in **content creation and media production**, **business and enterprise applications**, **accessibility and assistive technology**, and **personal and creative applications**. Creators and producers can create high-quality voiceovers, create multiple characters for storytelling, or produce content in their own voice when physically unavailable, all while simultaneously ensuring consistency in quality. Organizations can enhance customer experience and streamline communication processes, maintaining consistent service for customer support, marketing messages, or executive communications.

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

**Production Link:** https://voxify-prod.vercel.app/login

**Preview Link:** https://voxify-dev.vercel.app/login

--- 
Users can create an account and log in. Once they do so, they will be redirected to the user dashboard.

<p align="center">
<img src="https://imgur.com/rkQl6ho.png" width=48% alt= "Voxify registration">
<img src="https://imgur.com/ZubwDd8.png" width=48%alt="Voxify Login">
</p>

The dashboard has access to cloning your voice and the text-to-speech option, as well as statistics of your current voice clones and completed/processed tasks while the audio samples are recording. There is also a set of quick actions where users can view their tasks and profile settings.

<p align="center">
<img src="https://imgur.com/Iczav58.png" width=75% alt="Voxify dashboard" />
</p>

Users can clone their voice using a `.wav` audio sample of their own voice. A 10-second audio file is recommened. Once you name the voice, write a description, and include the reference text of what was said in the audio sample, it will be saved to your account.

<p align="center">
<img src="https://imgur.com/Ua78aC5.png" width=75% alt="Voxify voice generation page" />
</p>

The text-to-speech page allows users to input any text they want converted to audio using either a voice clone or the system voice(s). The user can also change the language spoken, as well as the speed, pitch, and volume the generated audio output will be when generated.

<p align="center">
<img src="https://imgur.com/GAMdDbm.png" width=75% alt="Voxify TTS page" />
</p>

Generated audio recordings are saved in the "Generated Voices" tab, and users can then download/play previously generated sound recordings.

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

# Development

This project is a **backend and frontend service service** using a Python/Flask backend, and a React/JavaScript frontend.

## Backend Structure

Voxify utilises a RESTful API structure. It uses Python and Flask with capabilities for the following:

- User authentication and management
- Voice sample upload and processing
- Voice clone generation and selection
- Text-to-speech synthesis with syllable-to-time or word-to-time mapping
- Synthesis job status monitoring
- Rate limiting and usage tracking

## Frontend Structure
#TODO (for Kiko)

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

- Docker Compose allows for multiple services to be run and compiled from individual Dockerfiles. A Dockerfile.base is used in the `backend/` for corresponding containers in to be built.
- Containers are orchestrated to make local development and testing easy to conduct.
- Integrations with the CI/CD pipeline are integrated for automated builds and testing. Using GitHub Actions, Formatting tests as well as tests for end-to-end API calls are tested to ensure branch merges do not affect existing test cases and the project is successful.

---

# Deployment
#TODO for Michael and Maddie

## Testing

## Local Deployment

---

# Project Task Management

 **GitHub Projects** is used to plan, track, and manage our development tasks, and the project boards will serve as the central hub for any work-related activities. Progress is checked and tasks are assigned each week during our weekly standups with our partner. Status of the project is also updated regularly and during the sync meetings.

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

## License

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