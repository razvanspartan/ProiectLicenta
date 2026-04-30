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
        decision = decision_maker.make_decision()
        print(decision)
        return {"message": f"{decision} made based on CPU usage."}, 200

    @app.route('/api/v1/decisionmaker/settings/<service_name>', methods=['GET'])
    def get_settings(service_name):
        decision_maker = decision_maker_factory.get_decision_maker(service_name)
        settings = decision_maker.get_settings()
        return {"settings": settings}, 200

    @app.route('/api/v1/decisionmaker/update_settings/<service_name>', methods=['POST'])
    def update_settings(service_name):
        data = request.get_json()
        decision_maker = decision_maker_factory.get_decision_maker(service_name)
        decision_maker.update_settings(data)
        return {"message": f"Settings updated for {service_name}."}, 200