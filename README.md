# Cloud-Native AI Inference Microservice

FastAPI serves a scikit-learn sentiment classifier for short English product reviews. The model fits a TF-IDF and logistic regression pipeline at startup using 40 original examples in `training_examples.py`. It is a classroom demo with no measured holdout accuracy.

## Run and test locally

```bash
docker build -t ai-inference-service .
docker volume create inference-data
docker run --rm -p 8080:8080 \
  -e SQLITE_PATH=/data/inference.db \
  -v inference-data:/data ai-inference-service
```

Or use Python 3.11 with `python -m pip install -r requirements.txt` and
`python -m uvicorn main:app --port 8080`.

Open [Swagger UI](http://localhost:8080/docs) or run:

```bash
curl -sS http://localhost:8080/
curl -sS http://localhost:8080/predict \
  -H 'Content-Type: application/json' \
  -d '{"text_input":"Excellent product and great quality","max_length":20}'
```

`text_input` accepts 1–2,000 characters. `max_length` limits the number of words passed to the model (1–200, default 50). Success returns the processed text, label, and request ID. Invalid input returns 422. A failed log write returns 503. The log stores the request ID, timestamp, label, processed text length, and model version.

## Deploy to Google Cloud Run

Use an authenticated Google Cloud CLI and a project with billing enabled. Set
`PROJECT_ID` to your project ID. The following setup assumes you can enable
APIs, create service accounts, and grant IAM roles.

```bash
PROJECT_ID='your-project-id'
REGION=us-central1
SA="inference-run@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com firestore.googleapis.com
gcloud iam service-accounts create inference-run --display-name="Inference runtime"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA" --role=roles/datastore.user
```

If the project has no default Firestore database, create one in Native mode.
Choose its location before creating it.

```bash
gcloud firestore databases create --database='(default)' \
  --location="$REGION" --type=firestore-native
```

From this directory, deploy the Dockerfile using Cloud Build:

```bash
gcloud run deploy ai-inference-service --source . --region "$REGION" \
  --service-account "$SA" --set-env-vars STORAGE_BACKEND=firestore \
  --allow-unauthenticated --max-instances 2
URL="$(gcloud run services describe ai-inference-service \
  --region "$REGION" --format='value(status.url)')"
curl -fsS "$URL/predict" -H 'Content-Type: application/json' \
  -d '{"text_input":"Terrible quality and very disappointing","max_length":20}'
```

Open `$URL/docs` and capture a successful request for the report. In the
Firestore console, look in `inference_logs` for a document with the returned
`request_id`. Capture the document and deployed service URL for cloud proof.
The runtime uses its assigned service account for Firestore.

See the official [Cloud Run source deployment guide](https://docs.cloud.google.com/run/docs/deploying-source-code)
for any Cloud Build service account permissions needed by your project.

## Publish and submit

Create a GitHub repository from these source files. With GitHub CLI signed in,
run the following from this directory:

```bash
git init -b main
git add .
git commit -m "Build AI inference capstone"
gh repo create ai-inference-service --public --source=. --remote=origin --push
```

Submit the GitHub repository URL, the Cloud Run HTTPS URL, and the PDF with
successful Swagger and Firestore evidence. Keep service account keys, local
databases, and other credentials out of the repository.
