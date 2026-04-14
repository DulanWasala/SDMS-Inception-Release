from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import get_connection

visitor_admin_bp = Blueprint("visitor_admin", __name__, url_prefix="/visitor-admin")

@visitor_admin_bp.route("/")
def index():
    return render_template("visitor_admin/index.html", title="Visitor System & Admin Panel")

@visitor_admin_bp.route("/temp-search", methods=["GET", "POST"])
def temp_search():
    results = []
    search_value = ""
    if request.method == "POST":
        search_value = request.form.get("search_value", "").strip()
        conn = get_connection()
        like_value = f"%{search_value}%"
        results = conn.execute(
            "SELECT * FROM temp_workers WHERE temp_id LIKE ? OR full_name LIKE ? ORDER BY full_name",
            (like_value, like_value),
        ).fetchall()
        conn.close()
    return render_template("visitor_admin/temp_search.html", results=results, search_value=search_value, title="Temp Worker Search")

@visitor_admin_bp.route("/temp/<int:temp_worker_id>")
def temp_profile(temp_worker_id):
    conn = get_connection()
    temp_worker = conn.execute("SELECT * FROM temp_workers WHERE id = ?", (temp_worker_id,)).fetchone()
    signins = conn.execute(
        "SELECT * FROM temp_signins WHERE temp_worker_id = ? ORDER BY sign_in_time DESC",
        (temp_worker_id,),
    ).fetchall()
    conn.close()
    if not temp_worker:
        flash("Temp worker not found.", "error")
        return redirect(url_for("visitor_admin.temp_search"))
    return render_template("visitor_admin/temp_profile.html", temp_worker=temp_worker, signins=signins, title="Temp Worker Profile")

@visitor_admin_bp.route("/temp-signin/<int:temp_worker_id>", methods=["GET", "POST"])
def temp_signin(temp_worker_id):
    conn = get_connection()
    temp_worker = conn.execute("SELECT * FROM temp_workers WHERE id = ?", (temp_worker_id,)).fetchone()
    if not temp_worker:
        conn.close()
        flash("Temp worker not found.", "error")
        return redirect(url_for("visitor_admin.temp_search"))
    if request.method == "POST":
        purpose = request.form.get("purpose", "").strip()
        issued_by = request.form.get("issued_by", "").strip()
        if not purpose or not issued_by:
            conn.close()
            flash("Please fill in all sign in details.", "error")
            return redirect(url_for("visitor_admin.temp_signin", temp_worker_id=temp_worker_id))
        sign_in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO temp_signins (temp_worker_id, sign_in_time, purpose, issued_by, status) VALUES (?, ?, ?, ?, ?)",
            (temp_worker_id, sign_in_time, purpose, issued_by, "Signed In"),
        )
        conn.commit()
        conn.close()
        flash(f"{temp_worker['full_name']} was successfully signed in.")
        return redirect(url_for("visitor_admin.temp_profile", temp_worker_id=temp_worker_id))
    conn.close()
    return render_template("visitor_admin/temp_signin.html", temp_worker=temp_worker, title="Temp Sign In")

@visitor_admin_bp.route("/signins")
def signins():
    conn = get_connection()
    rows = conn.execute(
        '''
        SELECT s.id, t.temp_id, t.full_name, t.company_name, s.sign_in_time, s.purpose, s.issued_by, s.status
        FROM temp_signins s
        JOIN temp_workers t ON t.id = s.temp_worker_id
        ORDER BY s.sign_in_time DESC
        '''
    ).fetchall()
    conn.close()
    return render_template("visitor_admin/signins.html", rows=rows, title="Temp Sign In Records")
