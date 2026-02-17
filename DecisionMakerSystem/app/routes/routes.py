from flask import request
from app.models.decision_maker_factory import DecisionMakerFactory

decision_maker_factory = DecisionMakerFactory()

def register_routes(app):
    @app.route('/api/v1/decisionmaker/scale/<service_name>', methods=['POST'])
    def attempt_scale(service_name):
        data = request.get_json()
        decision_maker = decision_maker_factory.get_decision_maker(service_name)
        cpu = data.get('cpu')
        decision_maker.add_prediction_point(cpu)
        decision_maker.make_decision()
