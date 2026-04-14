from flask import Flask, render_template
from db import init_db
from routes.equipment import equipment_bp
from routes.visitor_admin import visitor_admin_bp
from routes.lost_found import lost_found_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "sdms-secret-key"
    init_db()
    app.register_blueprint(equipment_bp)
    app.register_blueprint(visitor_admin_bp)
    app.register_blueprint(lost_found_bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
