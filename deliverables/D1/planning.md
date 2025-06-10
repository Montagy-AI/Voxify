# Voxify/ Majick
> _Note:_ This document will evolve throughout your project. You commit regularly to this file while working on the project (especially edits/additions/deletions to the _Highlights_ section). 
 > **This document will serve as a master plan between your team, your partner and your TA.**

## Product Details
 
#### Q1: What is the product?

We are building Voxify, a web-based tool and API that allows users to create voice clones and generate text-to-speech output using those voices. The platform supports multiple languages, emotional tone control, and zero-shot voice cloning, enabling both developers and content creators to generate expressive, customized speech effortlessly.
![b58dbae6be53116497e7c3dd3b277d3](https://github.com/user-attachments/assets/70f7337f-fc43-48c0-bffc-93ae278359ae)

#### Q2: Who are your target users?

1. Content creators and solo entrepreneurs who produce podcasts, videos, or social media content and want to create multilingual, expressive voiceovers using their own cloned voice.
Example persona: Sarah, a freelance YouTuber and language tutor who wants to generate videos in multiple languages using her own voice, without recording each version manually.
2. Developers and businesses that need to integrate text-to-speech or voice cloning into their applications via API.
Example persona: Leo, a software engineer working on an AI-powered video editing tool (like CutSmart) who needs a backend TTS engine with personalized voice capabilities.

![image](https://github.com/user-attachments/assets/1f50cd3f-8f29-4891-bebd-00600e5af9f0)

#### Q3: Why would your users choose your product? What are they using today to solve their problem/need?

We hope for Voxify to adddress the issues surrounding recording and localizing audio content across languages and platforms. With Voxify using **zero-shot voice cloning**, users will be able to generate a realistic, emotionally expressive clone of a voice using audio recordings that can be as short as a few seconds. This will drastically reduce the amount of time spent recording from hours to a few minutes. Creators can instantly produce voiceovers in multiple languages, whilst maintaining any unique vocal tones and styles that are desired. Voxify can also change generated voices to match different languages, accents, or emotional tones - something that can typically be costly, technically difficult, or simply unavailable. This is especially valuable for content creators or education platforms enhancing accessibility. 

Compared to traditional TTS tools or studio recordings, Voxify will offer scalable and developer-friendly APIs for seamless integration as a microservice, advanced features like word/syllable-to-time mapping, job tracking, and rate limiting, as well as robust security features like end-to-end encryption, secure authentication, and role-based access. These features would be critical for protecting voice data in enterprise environments. While some voice cloning and TTS platforms exist, we want Voxify to go beyond basic voice synthesis and deliver a combination of usability, flexibility, and scalability that is rare in the market.

#### Q4: What are the user stories that make up the Minumum Viable Product (MVP)?

1. **Multilingual Support and Emotion Control -** As an accessibility consultant, i want to use Voxify's API to translate our narrator's voice into another language (e.g., from English to Spanish) while keeping their original voice and emotions to maintain the original intended experience.
2. **Zero-Shot and Natural Sounding Capabilities -** As a game developer, I want to use Voxify to create dynamic NPCs that can have realistic and natural dialogue with the player.
3. **Low-Latency Voice Cloning -** As a healthcare app developer, I want to use the API to help my users with speech impairments quickly generate speech that matches their natural voice, so they can communicate more easily through my application.
4. **Usage Tracking and Developer Dashboard -** As an enterprise software developer, I want to use the API to provide usage analytics and rate limiting controls so I can monitor my application's voice synthesis costs and ensure fair usage across my user base.
5. **Word/Syllable-To-Time Mapping -** As a video editing app developer, I want the API to return precise timestamps for each word so I can automatically sync subtitles and visual effects with the generated speech in my application.
   ![image](https://github.com/user-attachments/assets/dce68352-ca01-40c9-b44c-3df632d5d294)


#### Q5: Have you decided on how you will build it? Share what you know now or tell us the options you are considering.

We have not completely decided how to build it quite yet, but we have some ideas of where to start and what we need:

## Technology Stack

For our backend, we're planning to use Python with Flask since it integrates well with AI/ML libraries and gives us the flexibility we need for voice processing. We'll most probably use SQLite for user management and voice sample metadata as recommended by our partner, along with a vector database like Chroma or Qdrant for storing voice embeddings. For the AI components, we're considering open-source TTS models. We arent sure which one yet, but preferably with librosa or some similar package for audio processing and resemblyzer for voice embedding extraction. We'll containerize everything using Docker with multi-stage builds and Docker Compose for local development, though we're still debating whether to use a single container or separate containers for the API server, AI processing, and databases.

## Architecture and Deployment

Our high-level architecture will include an API layer with Flask gRPC endpoints, an authentication service for user management, a voice processing service for handling uploads and embedding extraction, a TTS synthesis service for generating speech with timing data, and a storage layer combining SQLite, vector database, and cloud storage for audio files. We plan to deploy using cloud container services like AWS or GCP, with cloud storage for audio files and pre-trained models from Hugging Face. For CI/CD, we're looking at GitHub Actions with curl-based API testing as specified in the project requirements.

## Development Process

Our current rough-drafted plan for the development approach starts with defining API specifications, choosing our TTS model, and designing the database schema. Then we'll set up the Flask project with Docker and database configuration, followed by building API endpoints and integrating AI components. Finally, we'll implement security measures and CI/CD pipelines.

----
## Intellectual Property Confidentiality Agreement 

4. You will share the code under an open-source license and distribute it as you wish but only the partner can access the system deployed during the course.

We have agreed to option number 4, and the partner has specified that they do not mind sharing or giving access to systems outside, but the MIT license should be present. In their words, they don't mind us sharing the code as long as the MIT license is present.

----

## Teamwork Details

#### Q6: Have you met with your team?

We have met online, and have had a bunch of conversations on discord together. We've done a team-building activity online in the form of solving a 300 piece puzzle together (see image below) as well as talked about interests such as video games and past U of T courses. We also (for a little while before tutorial) did an artboard together. See the image for that below as well.

![image](https://github.com/user-attachments/assets/cfa197b9-0ad6-41d0-9752-a5769d54c201)
![image](https://github.com/user-attachments/assets/60606252-59fb-447d-b0b2-ab8b0f25ace7)

3 Fun facts about our team are that all of us have/do play League of Legends, around half of our team is currently working on completing a game design focus, and we all love cats!




#### Q7: What are the roles & responsibilities on the team?

1. Michael
* Roles: API Developer, Database Engineer, DevOps Engineer
* Responsibilities: Michael will contribute to designing and implementing API endpoints and database schemas, and will lead containerization efforts using Docker and CI/CD pipeline setup.
* Rationale: Michael is eager to deepen his DevOps skills, making him a strong fit for infrastructure tasks. He's also willing to devote time like more than 20 hours per week for this project.

2. Jaden
* Roles: API Developer, AI Engineer, DevOps Engineer
* Responsibilities: Jaden will assist in building gRPC interfaces, help containerize the backend system, and contribute to integrating voice synthesis models.
* Rationale: Jaden expressed strong interest in both infrastructure and AI technologies.
  
3. Kiko
* Roles: API Developer, Database Engineer, Code reviewer, develop manager
* Responsibilities: Kiko will work on implementing API routes, managing database interactions, and ensuring that the backend adheres to gRPC standards. Also, she is going to do the code review job and help debugging.
* Rationale: Kiko is also experienced in full-stack website dev and designing api endpoints. She also want to learn different tech stack by helping debugging.

4. Jun
* Roles: API Developer, Partner Liaison, Database Engineer
* Responsibilities: Jun will focus on writing efficient gRPC handlers and make sure it works well with database. He will also serve as the dedicated partner liaison, coordinating communications and maintaining meeting records.
* Rationale: Jun has a background in systems programming and is interested in being an project manager.
  
5. Maddie
* Roles: Security Lead, Containerization Support
* Responsibilities: Maddie will lead the implementation of authentication, access control, and encryption, and help with containerization tasks. 
* Rationale: Maddie is experienced with security aspect for developing and has experience in docker.

6. Chelsey
* Roles: AI Engineer, Database Engineer
* Responsibilities: Chelsey will help integrate TTS and voice embedding models and contribute to vector database design and optimization.
* Rationale: Chelsey has experience working with machine learning models and is particularly interested in the AI pipeline.

7. Amirali
* Roles: AI Engineer, Code reviewer, develop manager
* Responsibilities: Amirali will contribute to model selection, TTS pipeline integration, and help with fine-tuning models for voice synthesis. He is also responsible for reviewing code and debugging.
* Rationale: Amirali is passionate about deep learning and has experience working with pre-trained AI models, making him a good fit for AI components.


#### Q8: How will you work as a team?

1. Our team will hold a weekly team meeting every Friday at 6:00 PM (ET) to discuss progress, share updates, assign tasks, and address any blockers. These meetings will be held online and serve as our main sync point throughout the term.

2. In addition to formal meetings, we maintain two active group chats for the Voxify project — one on Slack and one on Discord. These are used for daily communication, informal discussions, task coordination, and quick Q&A. Task assignments and updates are frequently communicated in these channels to ensure smooth collaboration.

3. Each meeting will last approximately 1 hour and include:
 * Status updates from each member
 * Roadblock sharing and group problem-solving
 * Task reassignment and planning for the next sprint
 * Discussion of upcoming deliverables or partner feedback
 * Records are found at project-2-Voxify/deliverables/team/minutes
  
#### Q9: How will you organize your team?  

 * Artifacts for organizing the team:
   * Meeting minutes posted on Github
   * Github Backlog/Task Board to keep track of what needs to be completed —> provided by partner
   * Announcements made on Discord
   * How do you determine the status of work from inception to completion?
 * The team will usually prioritize tasks that our partner suggests for us to work on, but we will also discuss in our personal meetings the specific order of completion.
 * Tasks are assigned to team members depending on who is interested in working on what, what our area of focus is, and how much time we have to allocate for this project weekly.
 * The status of completion is determined by whether the feature we are implementing fulfills the requirements specified by the partner or not.

#### Q10: What are the rules regarding how your team works?

**Communications:**
 * We will use:
   * Slack for quick communication with the partner
   * Discord for team communication and meetings
   * Google Meet for our team calls with the partner (weekly)
 * Our project manager, Jun, is responsible for representing the team through lengthier emails
 
**Collaboration:**
 * Each team member is expected to attend meetings and complete the action items assigned to them. Continuous failure to do so would result in bad peer evaluations and a report to our assigned TA.
 * If a team member is unresponsive or not completing their work, the rest of the team will first try to understand the reason for this behavior. If it’s due to personal issues, they will offer support by reallocating tasks or extending deadlines. However, if the team member does not have a valid reason and refuses to change their behavior, the team will report the issue to the TA and/or address it in peer evaluations.

## Organisation Details

#### Q11. How does your team fit within the overall team organisation of the partner?

[//]: # (* Given the team structure of your partner, what role do you think your team will play?)

[//]: # (* Examples include product development that includes developing new features, or quality assurance that includes developing features that test the product reliability, or software maintenance that includes fixing crucial bugs in the product.)

[//]: # (* Provide examples of why you think you fit this role.)

Our team acts as the backend foundation of the Voxify project. While the partner is developing the frontend interface, we’re responsible for making sure the backend logic and systems work reliably and are ready to support user interactions.

We're developing the actual core of the product: voice cloning, TTS generation, data storage, and APIs that tie everything together. In that sense, we’re positioned as a product development team focused on core functionality.

#### Q12. How does your project fit within the overall product from the partner?

[//]: # (* Look at the big picture of the product and think about how your project fits into this product.)

[//]: # (* Is your project the first step towards building this product? Is it the first prototype? Are you developing the frontend of a product whose backend is developed by the partner? Are you building the release pipelines for a product that is developed by the partner? Are you building a core feature set and take full ownership of these features?)

[//]: # (* You should also provide details of who else is contributing to what parts of the product, if you have this information. This is more important if the project that you will be working on has strong coupling with parts that will be contributed to by members other than your team &#40;e.g., from a partner&#41;.)

[//]: # (* You can be creative for these questions and even use a graphical or pictorial representation to demonstrate the fit.)

[//]: # (* Briefly specify what your partner considers a success for this project. Do they want you to build specific features? Publish a usable product? Just a prototype? Be as specific as you can be at this point.)

Our project forms the first working prototype of the Voxify platform. It establishes the backend systems that enable the core functionality of the product: uploading voice samples, generating voice clones, and synthesizing speech with accurate word or syllable timing. This work lays the technical foundation that the partner’s frontend will build on.

While we are fully responsible for the backend, the partner is developing the frontend interface separately. The two parts are strongly connected — the frontend depends on the API endpoints we provide, and our backend must be flexible and reliable enough to support real user interaction.

According to our partner, success means delivering a backend that can pass a complete set of end-to-end API tests — including user registration, voice upload, clone generation, and speech synthesis with timestamped output. This will demonstrate that the platform’s key workflows are in place and functioning correctly.

## Potential Risks

#### Q13. What are some potential risks to your project?
Vague or Incomplete Specifications
* Explanation: The project intentionally provides vague requirements, which can lead to different interpretations by team members. This could result in inconsistencies in implementation, missing features, or misaligned expectations with the partner.

Different Paces or Misalignment Among Team Members
* Explanation: Team members may progress at different speeds or interpret tasks differently due to unclear requirements. This can cause integration issues, uneven workloads, and difficulty in meeting deadlines


#### Q14. What are some potential mitigation strategies for the risks you identified?
Vague or Incomplete Specifications
* Mitigation: Proactively collaborate with the partner and the team to create a detailed, shared specification document. Use diagrams, sample inputs/outputs, and clear definitions for each feature.

Different Paces or Misalignment Among Team Members
* Mitigation: Hold regular stand-up meetings to sync progress and clarify misunderstandings. Use task tracking tools (e.g., Trello, GitHub Projects) to ensure visibility of who’s doing what. Encourage open communication and collaborative work sessions.chan

