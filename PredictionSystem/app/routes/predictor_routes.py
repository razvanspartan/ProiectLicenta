from app.models.metric_collector_factory import MetricCollectorFactory

from app.models.VECM_predictor_factory import VECMPredictorFactory
from flask import request, jsonify

metric_collector_factory = MetricCollectorFactory()
vecm_predictor_factory = VECMPredictorFactory()

def register_routes(app):
    @app.route('/api/v1/predictor/metrics', methods=['POST'])
    def collect_metrics():
        data = request.get_json()
        service_name = data['service_name']
        metrics = data['metrics']
        metric_collector = metric_collector_factory.get_metric_collector(service_name)
        metric_collector.collect_metrics(metrics)
        vecm_predictor = vecm_predictor_factory.get_predictor(service_name)
        vecm_predictor.add_data(metrics)
        return jsonify({'message': 'metrics collected'}), 201