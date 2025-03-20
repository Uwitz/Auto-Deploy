import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
	data = await request.json()
	if data.headers.get("X-GitHub-Event") == "ping":
		return 200

	elif data.headers.get("X-GitHub-Event") == "push":
		repo_name = data.get("repository", {}).get("full_name", "")

		try:
			with open("config.json", "r") as f:
				config = json.load(f)

			for repo, path in config.get("repositories").items():
				if repo_name == repo:
					os.system(f"cd {path} && git pull")
					print(f"Pulled from repository: {repo_name}")
					return {"status": "deployed", "repository": repo_name}
			print(f"Ignoring push from repository: {repo_name}")
			return {"status": "ignored", "repository": repo_name}

		except Exception as e:
			print(f"Error reading config: {str(e)}")
			return {"status": "error", "message": str(e)}

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
