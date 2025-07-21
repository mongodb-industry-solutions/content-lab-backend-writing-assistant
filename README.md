# **Content Lab - Writing Assistant**

This repository hosts the backend microservice for the Writing Assistant, an AI-powered tool designed to help users draft, refine, and improve their written content. The service uses large language models (such as Anthropic Claude via AWS Bedrock) to provide real-time writing suggestions, content completions, and productivity tools for writers, editors, and content creators.

## **High Level Architecture**

[High level architecture diagram here use [google slides](https://docs.google.com/presentation/d/1vo8Y8mBrocJtzvZc_tkVHZTsVW_jGueyUl-BExmVUtI/edit#slide=id.g30c066974c7_0_3536)]

## **Architecture Overview**

This backend is structured as a modular microservice, focused on scalable, maintainable, and extensible AI-driven writing assistance. Each component is designed for independent development and integration with other services or frontends.

### Core Structure:

- **API Application:**

The main entry point `(backend/main.py)` serves as the API gateway, exposing endpoints for writing assistance, chat completions, and tool-based content operations. The API is designed for high performance and easy integration.

- **LLM Integration:**

The `(backend/bedrock/..)` directory contains modules for interacting with AWS Bedrock and Anthropic Claude models. These modules handle chat completions, prompt engineering, and communication with external AI services.

- **Writing Assistant Tools:**

The `(backend/writing_assistant/..)` directory provides specialized tools and logic for content help, editing, and enhancement. This includes utility functions, prompt templates, and workflow orchestration for writing tasks.

- **Client Abstraction::**

The `(backend/bedrock/client.py)` module abstracts the details of connecting to external AI services, ensuring secure and efficient communication.

- **Containerization:**

The service is fully containerized using Docker, enabling consistent deployment across environments.


## **Key Features**

- Real-time AI-powered writing suggestions and completions

- Modular toolset for content editing, rewriting, and enhancement

- Integration with Anthropic Claude and AWS Bedrock for advanced language capabilities

- API endpoints for seamless frontend integration

- Scalable, containerized deployment with Docker


## **Writing Assistant Workflow**

### Overview

1. **User Input:**  

Users submit a writing prompt, draft, or editing request via the frontend interface.

2. **Request Handling:**

The backend receives the request and routes it to the appropriate writing assistant tool or AI model.

3. **AI Processing:**

The service interacts with Anthropic Claude (via AWS Bedrock) to generate completions, suggestions, or edits based on the user’s input.

4. **Tool-Based Enhancement:**

Additional tools may process the AI output for grammar checking, style improvement, or formatting.

5. **Response Delivery:**

The content or suggestions are then returned to the user through the API.

**In summary:**  

The Writing Assistant backend combines user input, advanced AI models, and specialized tools to deliver high-quality writing assistance in real time.

## **Where Does MongoDB Shine?**




## **Tech Stack**

### Web Framework & API

- [**fastapi**](https://fastapi.tiangolo.com/) for API development and building REST endpoints.
- [**uvicorn**](https://www.uvicorn.org/) for running the ASGI server.

### Database & Data Storage
- [**pymongo**](https://pymongo.readthedocs.io/) for MongoDB connectivity and operations.

### AWS & Cloud Services
- [**boto3**](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) for AWS SDK integration and Bedrock API access.
- [**botocore**](https://botocore.amazonaws.com/v1/documentation/api/latest/index.html) for low-level AWS service operations.
- [**Anthropic Claude**](https://aws.amazon.com/bedrock/anthropic/?ams%23interactive-card-vertical%23pattern-data--1838624787.filter=%257B%2522filters%2522%253A%255B%255D%257D) via AWS Bedrock for text generation and content analysis.

### Containerization & Deployment

- [**Docker**](https://www.docker.com/) for containerized deployment.
- docker-compose for multi-service orchestration.

### Data Processing & Utilities
- [**python-dotenv**](https://python-dotenv.readthedocs.io/) for environment variable management.


## **Relevant Models**

- [**Claude 3 Haiku**](https://docs.aws.amazon.com/bedrock/latest/userguidebedrock-runtime_example_bedrock-runtime_InvokeModel_AnthropicClaude_section.html) for writing assisant. 


## **Key Components**

#### a. Bedrock Integration (`backend/bedrock/`)

- **anthropic_chat_completions.py:**  
  Handles chat completion requests to Anthropic Claude via AWS Bedrock.

- **client.py:**  
  Manages API client setup and secure communication with external AI services.

#### b. Writing Assistant Tools (`backend/writing_assistant/`)

- **assistant.py:**  
  Core logic for orchestrating writing assistance workflows.

- **tools.py:**  
  Utility functions and specialized tools for content editing and enhancement.

#### c. API Entrypoint (`backend/main.py`)

- Serves as the main API gateway, routing requests to the appropriate modules and tools.


## **Prerequisites**

Before you begin, ensure you have met the following requirements:

- **MongoDB Atlas** account - [Register Here](https://account.mongodb.com/account/register)
- **Python 3.10 or higher**
- **Poetry** – [Install Here](https://python-poetry.org/docs/#installation)
- **AWS CLI** configured with appropriate credentials – [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS Account** with Bedrock access enabled – [Sign up Here](https://aws.amazon.com/bedrock/)
- **Docker** (optional, for containerized deployment) – [Install Here](https://docs.docker.com/get-docker/)

---

## **Setup Instructions**

### 1. **Clone the Repository**

```bash
git clone <REPO_URL>
cd ist-media-internship-be2
```
> Replace `<REPO_URL>` with your repository's actual URL.

### 2. **Install Poetry**

If you don’t have Poetry installed, follow the [official installation guide](https://python-poetry.org/docs/#installation):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

---

### Step 2: Add MongoDB User

Follow [MongoDB's guide](https://www.mongodb.com/docs/atlas/security-add-mongodb-users/) to create a user with **readWrite** access to the `contentlab` database.

### 3. **Set Up Environment Variables**

> [!IMPORTANT]
> Create a `.env` file in the `/backend` directory with the following content:
>
> ```bash
> MONGODB_URI=your_mongod_uri
>DATABASE_NAME=dbname
>APP_NAME=appname
>NEWS_COLLECTION=news
>REDDIT_COLLECTION=reddit_posts
>SUGGESTION_COLLECTION=suggestions
>USER_PROFILES_COLLECTION=userProfiles
>DRAFTS_COLLECTION=drafts
>AWS_REGION=regionname
> ```

### 4. **Install Python Dependencies**

Navigate to the backend directory and install dependencies using Poetry:

```bash
cd backend
poetry install
```

---

### 5. **Run the Backend Service**

Start the backend API server:

```bash
poetry run python main.py
```
> If using FastAPI and Uvicorn, you might use:
> ```bash
> poetry run uvicorn main:app --host 0.0.0.0 --port 8000
> ```

---

### 6. **(Optional) Run with Docker**

To build and run the backend in a Docker container:

```bash
make build
```

To stop and remove the container and image:

```bash
make clean
```

---

### 7. **Access the API Documentation**

Once the server is running, open your browser and go to:

```
http://localhost:<PORT_NUMBER>/docs
```
E.g. `http://localhost:8001/docs`

> [!NOTE]
> Make sure to replace `<PORT_NUMBER>` with the port number you are using and ensure the backend is running.

## Common errors

> [!IMPORTANT]
> Check that you've created an `.env` file that contains the required environment variables.


---

**Troubleshooting Tips:**
- Ensure your `.env` file is present and correctly configured.
- Verify your AWS credentials and Bedrock access.
- If you encounter issues with dependencies, try `poetry lock --no-update` and then `poetry install` again.

---

You’re now ready to use the Writing Assistant Backend!

