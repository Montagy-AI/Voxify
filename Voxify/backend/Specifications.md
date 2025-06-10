# Voxify project

_Voxify_ aims to be a platform for Voice Cloning and Text-to-Speech (TTS) synthesis. The project will focus on creating a user-friendly interface for users to upload their voice samples and generate synthetic speech. In this project, we will use the latest open-source models and libraries to ensure high-quality voice synthesis. This project has a backend and a frontend. CSC301 students will work on the backend. Frontend is not part of the project for CSC301 students.

This specification document outlines the requirements and features of the Voxify project. The project will be developed using **Python** and **Flask** for the backend, and it will utilize various open-source libraries for voice synthesis. The project will also include a database to store user information and voice samples.

Specifications are left vague intentionally to allow for flexibility in implementation as well as test the team's ability to write robust and sound specification documents. The goal is to create a robust and scalable platform that can handle multiple users and provide high-quality voice synthesis. Part of the requirements will be my collaboration with the team to have come-up fine-tune these specifications.

## Project Overview

### Containerization

Voxify will be containerized using Docker to ensure consistent deployment across different environments. The containerization strategy includes:

- Decision to use a single container for AI, Database, and web server is up to the team. Multiple containers may be advantageous for for faster development due to various open-source libraries and models coming with out-of-the-box support with docker and specific versions of libraries and Python.
- Docker Compose for local development and testing
- Container orchestration for production deployment
- CI/CD pipeline integration for automated builds and testing

### AI Components

The core AI functionality of Voxify will leverage:

- Pre-trained voice synthesis models for TTS generation.
- Voice embedding extraction for personalized cloning
- Fine-tuning capabilities for improved voice quality
- Real-time processing for immediate feedback
- Model versioning and management for continuous improvement
- Syllable-to-time or word-to-time mapping for accurate timing and intonation.

### Database

Voxify will use two seperate databases: a Relational database for user management and storage of voice samples, and a Vector database for storing voice embeddings.

### API Structure

Voxify will provide a RESTful API with the following capabilities:

- User authentication and management
- Voice sample upload and processing
- Voice clone generation and selection
- Text-to-speech synthesis with syllable-to-time or word-to-time mapping
- Synthesis job status monitoring
- Rate limiting and usage tracking

### Security Considerations

The platform will implement robust security measures including:

- End-to-end encryption for voice data
- Secure user authentication
- Role-based access control
- Data anonymization for privacy

### Testing

Testing should be done via CI/CD pipelines. Tests should be either single end-to-end API test via `curl` or series of calls for specific user stories. Passing the tests is the measure of the success for this project.

Here is some examples for the tests:

- User sign-up API calls
- User login API calls
- User uploads a new voice to clone
- User sees the list of voices they have cloned
- User uploads a text with the ID of a cloned voice and get the converted text to speech with the timestamps of each word/syllable 