use axum::{
    extract::State,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex}; // Add Mutex for thread-safe updates

struct AppState {
    vault_url: String,
    client: reqwest::Client,
    current_context: Mutex<String>, // New: This stores your active window
}

#[derive(Deserialize, Serialize)]
struct IngestionRequest {
    content: String,
    category: String,
    tags: Vec<String>,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let shared_state = Arc::new(AppState {
        vault_url: "http://localhost:8001/ingest".to_string(),
        client: reqwest::Client::new(),
        current_context: Mutex::new("Desktop".to_string()),
    });

    let app = Router::new()
        .route("/health", get(health_check))
        .route("/proxy/ingest", post(proxy_ingest))
        .route("/state/update", post(update_state)) // New: Endpoint for Sentinel
        .route("/query", get(query_kernel))
        .route("/command/listen", post(toggle_listen))
        .with_state(shared_state);

    let addr = std::net::SocketAddr::from(([127, 0, 0, 1], 3000));
    tracing::info!("Monday Orchestrator active on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn toggle_listen(State(state): State<Arc<AppState>>) -> axum::http::StatusCode {
    let _ = state.client.post("http://localhost:8003/toggle").send().await;
    axum::http::StatusCode::OK
}

async fn health_check() -> &'static str {
    "Monday Kernel Orchestrator: Online"
}

async fn proxy_ingest(
    State(state): State<Arc<AppState>>,
    // We "unwrap" the Json wrapper here using parentheses
    axum::extract::Json(mut payload): axum::extract::Json<IngestionRequest>,
) -> Result<Json<serde_json::Value>, (axum::http::StatusCode, String)> {

    // 1. Get the current window from state
    let current_window = state.current_context.lock().unwrap().clone();

    // 2. Now 'payload' is just the raw IngestionRequest struct, so we can modify it
    payload.tags.push(format!("context:{}", current_window));

    // 3. Forward the raw struct to the Python Vault Agent
    let response = state.client
        .post(&state.vault_url)
        .json(&payload) // This now works because payload is the struct, not the wrapper!
        .send()
        .await
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // 2. Capture the status as a raw u16 to bridge the version gap
    let status_raw = response.status().as_u16();

    // 3. Convert that u16 into the Version of StatusCode Axum understands
    let axum_status = axum::http::StatusCode::from_u16(status_raw)
        .unwrap_or(axum::http::StatusCode::INTERNAL_SERVER_ERROR);

    let body = response.json::<serde_json::Value>()
        .await
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    if axum_status.is_success() {
        Ok(Json(body))
    } else {
        Err((axum_status, "Vault Agent returned an error".to_string()))
    }
}

async fn update_state(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<serde_json::Value>,
) -> axum::http::StatusCode {
    if let Some(window) = payload.get("window").and_then(|w| w.as_str()) {
        let mut context = state.current_context.lock().unwrap();
        *context = window.to_string();
        tracing::info!("🧠 Kernel Context Updated: {}", window);
        axum::http::StatusCode::OK
    } else {
        axum::http::StatusCode::BAD_REQUEST
    }
}

async fn query_kernel(
    State(state): State<Arc<AppState>>,
    axum::extract::Query(params): axum::extract::Query<std::collections::HashMap<String, String>>,
) -> Result<Json<serde_json::Value>, (axum::http::StatusCode, String)> {
    let query_text = params.get("q").cloned().unwrap_or_default();

    let vault_recall_url = format!("http://localhost:8001/recall?query={}", query_text);

    let response = state.client
        .get(&vault_recall_url)
        .send()
        .await
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let body = response.json::<serde_json::Value>()
        .await
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(body))
}