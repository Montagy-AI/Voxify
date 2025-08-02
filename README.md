# Voxify

Voxify is an AI-powered voice cloning and text-to-speech platform that enables users to create personalized synthetic voices from audio samples. The application leverages cutting-edge diffusion transformer technology (F5-TTS) to generate high-quality, natural-sounding speech that mimics individual voice characteristics.

**Context & Value:** Voice cloning technology addresses the growing demand for personalized audio content across multiple industries. Traditional TTS systems produce generic, robotic voices that lack emotional nuance and personal connection. Voxify solves this by democratizing voice synthesis technology, making it accessible through a user-friendly API while maintaining enterprise-grade security and performance standards.

The platform's value lies in its ability to preserve human vocal identity digitally, enabling content creators, businesses, and individuals to scale personalized audio production without sacrificing authenticity or quality.


---

## Partner Information:
Mehdi Zeinali  
Engineer of Computer Vision, Network Security and Embedded Solutions  
📧: mehdi@zeina.li  
☎️️: 778-952-3223  


---

## Overview
Voxify's core capabilities consist of voice sample processing, embedding generation, real-time synthesis, and precise timing control for natural speech patterns.

---
Users can create an account and log in. Once they do so, they will be redirected to the user dashboard.
<img src="https://github.com/user-attachments/assets/4260418f-962e-4fc0-8a36-41ee51465aee" width=49.5% alt="Voxify register" />
<img src="https://github.com/user-attachments/assets/f84c035e-9e75-4f0b-ab6c-a62f6cfd1243" width=49.5% alt="Voxify login" />

<img src="https://github.com/user-attachments/assets/ab149e10-7f5f-41f5-9367-65aa9bfe62a0" alt="Voxify dashboard">

The dashboard has access to cloning your voice and the text-to-speech option, as well as statistics of your current voice clones and completed/processed tasks while the audio samples are recording. There is also a set of quick actions where users can view their tasks and profile settings.

Users can clone their voice using a `.wav` audio sample of their own voice. A 10-second audio file is recommened. Once you name the voice, write a description, and include the reference text of what was said in the audio sample, it will be saved to your account.

![image](https://github.com/user-attachments/assets/86dafce4-fd21-457e-8e92-3e2a38fd0ca5)

The text-to-speech page allows users to input any text they want converted to audio using either a voice clone or the system voice(s). The user can also change the language spoken, as well as the speed, pitch, and volume the generated audio output will be when generated.

![image](https://github.com/user-attachments/assets/81692ae7-ed54-4d8c-9a68-a1d850896cac)

Generated audio recordings are saved in the "Generated Voices" tab, and users can then download/play previously generated sound recordings.

![image](https://github.com/user-attachments/assets/858e9e14-9c51-4d41-8d13-769c20dc7949)

There is an accessibility widget in the bottom right corner that allows users to customize their view to better suit individual needs.

![image](https://github.com/user-attachments/assets/feadf6f8-83e4-4408-ae26-475ee932f5d9)

The customizable options include adhering to accessibility profiles, content adjustments, color adjustments, and orientation adjustments.
<img src="https://github.com/user-attachments/assets/74853281-b047-4650-b4fc-f98f58c3ea52" width=27% />
<img src="https://github.com/user-attachments/assets/22e11b3b-a456-46c0-a90b-918ca9ed028a" width=22% />
<img src="https://github.com/user-attachments/assets/11790a18-cb98-4dfb-9739-e207257417c9" width=25% />
<img src="https://github.com/user-attachments/assets/65593945-df04-4bcd-ba6a-33f9805d6772" width=24% />

---

### Key Use Cases

This project hopes to aid primarily in **content creation and media production**, **business and enterprise applications**, **accessibility and assistive technology**, and **personal and creative applications**. Creators and producers can create high-quality voiceovers, create multiple characters for storytelling, or produce content in their own voice when physically unavailable, all while simultaneously ensuring consistency in quality. Organizations can enhance customer experience and streamline communication processes, maintaining consistent service for customer support, marketing messages, or executive communications.

Beyond professional use, Voxify enables personal expression and memory preservation with voice manipulation, character creation, and other settings to preserve loved ones' voices or create fictional voices for creative expression. Additionally, accessibility needs can also be met by providing individuals with speech impairments or language barriers the opportunity to recreate their original voice in speech for their original language or others while preserving vocal identity.

### Key Features
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

## Getting Started

**Link to the application:** https://voxify-front.vercel.app/login

First register for an account, then log in. Be sure that your password includes a number, capital letter, and special character.

Once you have done so, upload a `.wav` audio recording of your voice so it gets cloned and saved. You can then use the the text-to-speech option to generate a new recording with the sampled voice.


---

### Development

This project is a **backend service** exposed through RESTful APIs using **Flask**. It is intended to be consumed by external frontend clients or integrated into other platforms. API usage documentation will be added in the `D1/mock` directory as the first design, will be evolved while developing.

#### Containerization
Docker is used for containerization:
- Docker Compose allows for multiple services to be run and compiled from individual Dockerfiles. A Dockerfile.base is used in the `backend/` for corresponding containers in to be built.
- Containers are orchestrated to make local development and testing easy to conduct.
- Integrations with the CI/CD pipeline are integrated for automated builds and testing. Using GitHub Actions, Formatting tests as well as tests for end-to-end API calls are tested to ensure branch merges do not affect existing test cases and the project is successful.

#### API Structure
Voxify utilises a RESTful API structure. It uses Python and Flask with capabilities for the following:
- User authentication and management
- Voice sample upload and processing
- Voice clone generation and selection
- Text-to-speech synthesis with syllable-to-time or word-to-time mapping
- Synthesis job status monitoring
- Rate limiting and usage tracking

#### Databases
Voxify uses two databases - a relational database for user management and storage of voice samples, and a vector database for storing voice embeddings.
- SQLite is used to store user profiles, authentication data, and metadata, as well as their uploaded voices.
- ChromaDB is used for storing and querying voice embeddings, each with metadata linking it back to corresponding users or tasks.

#### AI Components
The AI functionality of Voxify uses voice synthesis models used for text-to-speech (TTS) generation. We are currently using F5-TTS, which is an open-source TTS synthesis tool using diffusion transformers.
- Voice embeddings are extracted for personalized cloning.
- There will be fine-tuning capabiltiies for improved voice quality.
- Real-time processing is used for immediate feedback.
- There are also plans for model versioning/management, and syllable-to-time or word-to-time mapping for accurate timing and intonation.


---

## Project Task Management

 **GitHub Projects** is used to plan, track, and manage our development tasks, and the project boards will serve as the central hub for any work-related activities. Progress is checked and tasks are assigned each week during our weekly standups with our partner. Status of the project is also updated regularly and during the sync meetings.

### GitHub Workflow Overview

- **Sprints -** We are operating on a 1-week sprint-based development, where each member is assigned a task to complete for that week. New tasks are added based on our goals and requirements for upcoming milestones, and they may carryover from previous sprints depending on the progress made.
- **Tasks & Issues -** Each task is created as a GitHub issue and is linked to the project board. We assign each task to the member and include the necessary milestones and labels to it. Any development-related tasks also get linked to a new branch beginning with `pr/[ISSUE]`.
- **Labels -** All tasks are labelled based on different types, as a feature, bug, enhcancement, or documentation, as well as a start-to-end date to ensure that all members understand what is being worked on.
- **Project boards -** Columns are divided as "To Do", "In Progress", "Done", where each task gets moved along to reflect current progress. There is also a "Backburner" column for any features that may be considered later on in development but are not a priority.
- **Automation -** GitHub automation is used using CI/CD workflows, ensuring that all issues and pull requests can be synced with the board status and do not have any problems before being pushed to the main branch.


---

## License

This project is currently licensed under the MIT License.

We deicided to release under an open-source MIT License to encourage adoption and changes to our project as we continue development. It will allow users to freely use, modify, and integrate our technology using only basic attribution. We hope that this project can be an opportunity for individual developers and startup companies to experiment and work on issues surrounding AI and voice synthesis.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
