# YOUR PRODUCT/TEAM NAME
> _Note:_ This document will evolve throughout your project. You commit regularly to this file while working on the project (especially edits/additions/deletions to the _Highlights_ section). 
 > **This document will serve as a master plan between your team, your partner and your TA.**

## Product Details
 
#### Q1: What is the product?

 > Short (1 - 2 min' read)
 * Start with a single sentence, high-level description of the product.
 * Be clear - Describe the problem you are solving in simple terms.
 * Specify if you have a partner, who they are (role/title), and the organization information.
 * Be concrete. For example:
    * What are you planning to build? Is it a website, mobile app, browser extension, command-line app, etc.?      
    * When describing the problem/need, give concrete examples of common use cases.
    * Assume the reader knows nothing about the partner or the problem domain and provide the necessary context. 
 * Focus on *what* your product does, and avoid discussing *how* you're going to implement it.      
   For example: This is not the time or the place to talk about which programming language and/or framework you are planning to use.
 * **Feel free (and very much encouraged) to include useful diagrams, mock-ups and/or links**.


#### Q2: Who are your target users?

  > Short (1 - 2 min' read max)
 * Be specific (e.g. a 'a third-year university student taking CSC301 and studying Computer Science' and not 'a student')
 * **Feel free to use personas. You can create your personas as part of this Markdown file, or add a link to an external site (for example, [Xtensio](https://xtensio.com/user-persona/)).**

#### Q3: Why would your users choose your product? What are they using today to solve their problem/need?

> Short (1 - 2 min' read max)
 * We want you to "connect the dots" for us - Why does your product (as described in your answer to Q1) fits the needs of your users (as described in your answer to Q2)?
 * Explain the benefits of your product explicitly & clearly. For example:
    * Save users time (how and how much?)
    * Allow users to discover new information (which information? And, why couldn't they discover it before?)
    * Provide users with more accurate and/or informative data (what kind of data? Why is it useful to them?)
    * Does this application exist in another form? If so, how does your differ and provide value to the users?
    * How does this align with your partner's organization's values/mission/mandate?

#### Q4: What are the user stories that make up the Minumum Viable Product (MVP)?

 * At least 5 user stories concerning the main features of the application - note that this can broken down further
 * You must follow proper user story format (as taught in lecture) ```As a <user of the app>, I want to <do something in the app> in order to <accomplish some goal>```
 * User stories must contain acceptance criteria. Examples of user stories with different formats can be found here: https://www.justinmind.com/blog/user-story-examples/. **It is important that you provide a link to an artifact containing your user stories**.
 * If you have a partner, these must be reviewed and accepted by them. You need to include the evidence of partner approval (e.g., screenshot from email) or at least communication to the partner (e.g., email you sent)

#### Q5: Have you decided on how you will build it? Share what you know now or tell us the options you are considering.

> Short (1-2 min' read max)
 * What is the technology stack? Specify languages, frameworks, libraries, PaaS products or tools to be used or being considered. 
 * How will you deploy the application?
 * Describe the architecture - what are the high level components or patterns you will use? Diagrams are useful here. 
 * Will you be using third party applications or APIs? If so, what are they?

We have not completely decided how to build it quite yet, but we have some ideas of where to start and what we need.

## Technology Stack

For our backend, we're planning to use Python with Flask since it integrates well with AI/ML libraries and gives us the flexibility we need for voice processing. We'll most probably use SQLite for user management and voice sample metadata as recommended by our partner, along with a vector database like Chroma or Qdrant for storing voice embeddings. For the AI components, we're considering open-source TTS models. We arent sure which one yet, but preferably with librosa or some similar package for audio processing and resemblyzer for voice embedding extraction. We'll containerize everything using Docker with multi-stage builds and Docker Compose for local development, though we're still debating whether to use a single container or separate containers for the API server, AI processing, and databases.

## Architecture and Deployment

Our high-level architecture will include an API layer with Flask gRPC endpoints, an authentication service for user management, a voice processing service for handling uploads and embedding extraction, a TTS synthesis service for generating speech with timing data, and a storage layer combining SQLite, vector database, and cloud storage for audio files. We plan to deploy using cloud container services like AWS or GCP, with cloud storage for audio files and pre-trained models from Hugging Face. For CI/CD, we're looking at GitHub Actions with curl-based API testing as specified in the project requirements.

## Development Process

Our current rough-drafted plan for the development approach starts with defining API specifications, choosing our TTS model, and designing the database schema. Then we'll set up the Flask project with Docker and database configuration, followed by building API endpoints and integrating AI components. Finally, we'll implement security measures and CI/CD pipelines.

----
## Intellectual Property Confidentiality Agreement 
> Note this section is **not marked** but must be completed briefly if you have a partner. If you have any questions, please ask on Piazza.
>  
**By default, you own any work that you do as part of your coursework.** However, some partners may want you to keep the project confidential after the course is complete. As part of your first deliverable, you should discuss and agree upon an option with your partner. Examples include:
1. You can share the software and the code freely with anyone with or without a license, regardless of domain, for any use.
2. You can upload the code to GitHub or other similar publicly available domains.
3. You will only share the code under an open-source license with the partner but agree to not distribute it in any way to any other entity or individual. 
4. You will share the code under an open-source license and distribute it as you wish but only the partner can access the system deployed during the course.
5. You will only reference the work you did in your resume, interviews, etc. You agree to not share the code or software in any capacity with anyone unless your partner has agreed to it.

**Your partner cannot ask you to sign any legal agreements or documents pertaining to non-disclosure, confidentiality, IP ownership, etc.**

Briefly describe which option you have agreed to.

----

## Teamwork Details

#### Q6: Have you met with your team?

Do a team-building activity in-person or online. This can be playing an online game, meeting for bubble tea, lunch, or any other activity you all enjoy.
* Get to know each other on a more personal level.
* Provide a few sentences on what you did and share a picture or other evidence of your team building activity.
* Share at least three fun facts from members of your team (total not 3 for each member).

We have met online, and have had a bunch of conversations on discord together. We've done a team-building activity online in the form of solving a 300 piece puzzle together (see image below) as well as talked about interests such as video games and past U of T courses. We also (for a little while before tutorial) did an artboard together. See the image for that below as well.

![image](https://github.com/user-attachments/assets/cfa197b9-0ad6-41d0-9752-a5769d54c201)
![image](https://github.com/user-attachments/assets/60606252-59fb-447d-b0b2-ab8b0f25ace7)

3 Fun facts about our team are that all of us have/do play League of Legends, around half of our team is currently working on completing a game design focus, and we all love cats!




#### Q7: What are the roles & responsibilities on the team?

Describe the different roles on the team and the responsibilities associated with each role. 
 * Roles should reflect the structure of your team and be appropriate for your project. One person may have multiple roles.  
 * Add role(s) to your Team-[Team_Number]-[Team_Name].csv file on the main folder.
 * At least one person must be identified as the dedicated partner liaison. They need to have great organization and communication skills.
 * Everyone must contribute to code. Students who don't contribute to code enough will receive a lower mark at the end of the term.

List each team member and:
 * A description of their role(s) and responsibilities including the components they'll work on and non-software related work
 * Why did you choose them to take that role? Specify if they are interested in learning that part, experienced in it, or any other reasons. Do no make things up. This part is not graded but may be reviewed later.


#### Q8: How will you work as a team?

Describe meetings (and other events) you are planning to have. 
 * When and where? Recurring or ad hoc? In-person or online?
 * What's the purpose of each meeting?
 * Other events could be coding sessions, code reviews, quick weekly sync meeting online, etc.
 * You should have 2 meetings with your project partner (if you have one) before D1 is due. Describe them here:
   * You must keep track of meeting minutes and add them to your repo under "deliverables/minutes" folder
   * You must have a regular meeting schedule established for the rest of the term.  
  
#### Q9: How will you organize your team?

List/describe the artifacts you will produce to organize your team. (We strongly recommend that you use standard collaboration tools like Linear.app, Jira, Slack, Discord, GitHub.)       

 * Artifacts can be To-Do lists, Task boards, schedule(s), meeting minutes, etc.
 * We want to understand:
   * How do you keep track of what needs to get done? (You must grant your TA and partner access to systems you use to manage work)
   * **How do you prioritize tasks?**
   * How do tasks get assigned to team members?
   * How do you determine the status of work from inception to completion?

#### Q10: What are the rules regarding how your team works?

**Communications:**
 * What is the expected frequency? What methods/channels will be used? 
 * If you have a partner project, what is your process for communicating with your partner? Who is responsible?
 
**Collaboration: (Share your responses to Q8 & Q9 from A1)**
 * How are people held accountable for attending meetings, completing action items? what is your process?
 * How will you address the issue if one person doesn't contribute or is not responsive?

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
* Now that you have defined your project, what risks can you identify that might impact it?
* Some examples of risks at this planning stage could include:
  * Uncertainties regarding a specific feature
  * Misaligned expectations or conflicts
  * Lack of clarity in execution or decision-making
  * Limited access to data, systems, or other dependencies
  * User stories that are too abstract or too simple
* For each risk, provide a brief bullet point and then explain the risk in detail. 

#### Q14. What are some potential mitigation strategies for the risks you identified?
* Examples of mitigation strategies:
  * More communication with the partner might help with improving clarity.
  * Adding more details for an user story might make it less abstract.
  * Adding an extra user story might increase the project complexity, making it less simple.
* It's ok if you are unable to find mitigation strategies for all the risks right now.
