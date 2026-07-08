# =============================================================================
# LEARNING MODULE: Docker Multi-Stage Builds
# =============================================================================
# Multi-stage builds are used to optimize Docker images by separating the 
# build environment from the runtime environment.
# 
# Stage 1 (Builder): We use a Node.js image to install dependencies and build 
# the React frontend. The resulting static files are saved in the `dist/` folder.
# 
# Stage 2 (Runtime): We use a lightweight Python image to run our FastAPI backend.
# We copy ONLY the built `dist/` folder from Stage 1, completely discarding 
# Node.js and the frontend source code. This makes the final image much smaller 
# and more secure!
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Build the React Frontend
# -----------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy package.json and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source code and build it
COPY frontend/ ./
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Build the Python Backend & Serve
# -----------------------------------------------------------------------------
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend API code
COPY backend/ ./backend/

# Copy the built React files from Stage 1 into the location the API expects them
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
