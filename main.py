import uvicorn
import json
import os
from typing import List
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class RepositoryConfig(BaseModel):
	path: str
	branch: str
	commands: List[str]

class Config(BaseModel):
	repositories: dict[str, RepositoryConfig]

app = FastAPI(
	title="AutoDeploy API",
	description="API for AutoDeploy",
	version="1.0.0"
)

app.add_middleware(
	CORSMiddleware,
	allow_origins = ["*"],
	allow_credentials = True,
	allow_methods = ["*"],
	allow_headers = ["*"],
)

@app.get("/health")
async def health_check():
	return {"online": True}

@app.post("/deploy")
async def deploy(request: Request):
	try:
		event_type = request.headers.get("X-GitHub-Event")
		if not event_type:
			raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")

		if event_type == "ping":
			return {"status": "ok", "message": "Ping received"}

		if event_type == "push":
			payload = await request.json()
			repo_name = payload.get("repository", {}).get("full_name", "")
			ref = payload.get("ref", "").replace("refs/heads/", "")

			if not repo_name:
				raise HTTPException(status_code=400, detail="Repository name not found in payload")

			try:
				with open("config.json", "r") as f:
					config_data = json.load(f)
					config = Config(**config_data)
			except Exception as e:
				raise HTTPException(status_code=500, detail=f"Error reading config: {str(e)}")

			repo_config = config.repositories.get(repo_name)
			if not repo_config:
				return {"status": "ignored", "message": f"Repository {repo_name} not configured"}

			if ref != repo_config.branch:
				return {"status": "ignored", "message": f"Push to branch {ref} ignored, configured for {repo_config.branch}"}

			try:
				os.chdir(repo_config.path)
				
				os.system("git pull")
				print(f"Pulled from repository: {repo_name}")

				for command in repo_config.commands:
					if command.strip():
						os.system(command)
						print(f"Executed command: {command}")

				return {
					"status": "success",
					"repository": repo_name,
					"branch": ref,
					"message": "Deployment completed successfully"
				}

			except Exception as e:
				raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

		return {"status": "ignored", "message": f"Unsupported event type: {event_type}"}

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
