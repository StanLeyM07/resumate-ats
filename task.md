# Project Roadmap & Timeline

This document tracks the execution plan and timeline for completing the final phase of the ResuMate ATS.

## Phase 2: Full-Stack Dockerization (Estimated: 15 minutes)
**Goal:** Containerize the application for one-click deployment using a multi-stage build.
- `[x]` **Configuration:** Create `.dockerignore` at project root (exclude `node_modules`, `__pycache__`, `.venv`, `ats.db`, `.env`).
- `[x]` **Dockerfile:** Create `Dockerfile` at project root:
  - *Stage 1 (Node):* Copy `frontend`, run `npm install` and `npm run build`.
  - *Stage 2 (Python):* Copy backend code, install `requirements.txt`.
  - *Integration:* Copy the `dist` folder from Stage 1 to the backend's expected directory.
  - *Runtime:* Expose port 8000 and run Uvicorn.
- `[x]` **Documentation:** Update `README.md` with instructions on how to build and run the Docker container.

## Phase 3: System Testing (Estimated: 10 minutes)
**Goal:** Verify the system operates flawlessly within the Docker container.
- `[x]` **Build:** Run `docker build -t resumate-app .`
- `[x]` **Run:** Run `docker run --env-file .env -p 8000:8000 resumate-app`
- `[ ]` **Test:** Create a test role, upload candidates, and verify the AI scores them successfully using the containerized API.

## Phase 4: Public Deployment (Estimated: 20 minutes)
**Goal:** Deploy the containerized application to a cloud hosting provider to generate a public link.
- `[ ]` **Provider Selection:** Choose a hosting platform that supports Docker containers (e.g., Render, Railway, Heroku, or AWS App Runner).
- `[ ]` **Preparation:** Push the project repository to GitHub or connect the local Docker image to the platform's container registry.
- `[ ]` **Deployment:** Deploy the Docker container to the cloud platform, ensuring port 8000 maps correctly to the web service.
- `[ ]` **Verification:** Access the generated public link and run a final end-to-end test on the live production URL.

---
**Current Status:** Docker container is running locally! Awaiting manual testing of Phase 3 before moving to Phase 4.
