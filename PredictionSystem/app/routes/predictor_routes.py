import threading

from app.services.collection_service import collect_metrics


def register_routes(app):
    threading.Thread(target=collect_metrics, daemon=True).start()
