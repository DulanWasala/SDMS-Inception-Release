from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import get_connection

equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")

@equipment_bp.route("/search", methods=["GET", "POST"])
def employee_search():
    results = []
    search_value = ""
    if request.method == "POST":
        search_value = request.form.get("search_value", "").strip()
        conn = get_connection()
        like_value = f"%{search_value}%"
        results = conn.execute(
            "SELECT * FROM employees WHERE employee_id LIKE ? OR full_name LIKE ? ORDER BY full_name",
            (like_value, like_value),
        ).fetchall()
        conn.close()
    return render_template("equipment/employee_search.html", results=results, search_value=search_value, title="Employee Search")

@equipment_bp.route("/employee/<int:employee_id>")
def employee_profile(employee_id):
    conn = get_connection()
    employee = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    current_assignments = conn.execute(
        '''
        SELECT e.equipment_code, e.equipment_type, e.item_profile, t.checkout_time, t.checkout_condition
        FROM checkout_transactions t
        JOIN equipment e ON e.id = t.equipment_id
        WHERE t.employee_id = ? AND t.return_time IS NULL
        ORDER BY t.checkout_time DESC
        ''',
        (employee_id,),
    ).fetchall()
    conn.close()
    if not employee:
        flash("Employee not found.", "error")
        return redirect(url_for("equipment.employee_search"))
    return render_template("equipment/employee_profile.html", employee=employee, current_assignments=current_assignments, title="Employee Profile")

@equipment_bp.route("/checkout/<int:employee_id>", methods=["GET", "POST"])
def equipment_checkout(employee_id):
    conn = get_connection()
    employee = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    available_equipment = conn.execute("SELECT * FROM equipment WHERE status = 'Available' ORDER BY equipment_type, equipment_code").fetchall()
    if not employee:
        conn.close()
        flash("Employee not found.", "error")
        return redirect(url_for("equipment.employee_search"))

    if request.method == "POST":
        equipment_id = request.form.get("equipment_id")
        checkout_condition = request.form.get("checkout_condition", "").strip()
        issued_by = request.form.get("issued_by", "").strip()
        equipment = conn.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,)).fetchone()

        if not equipment:
            conn.close()
            flash("Selected equipment was not found.", "error")
            return redirect(url_for("equipment.equipment_checkout", employee_id=employee_id))
        if equipment["status"] != "Available":
            conn.close()
            flash("That equipment is not available.", "error")
            return redirect(url_for("equipment.equipment_checkout", employee_id=employee_id))
        if not checkout_condition or not issued_by:
            conn.close()
            flash("Please fill in all checkout details.", "error")
            return redirect(url_for("equipment.equipment_checkout", employee_id=employee_id))

        checkout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO checkout_transactions (employee_id, equipment_id, issued_by, checkout_condition, checkout_time) VALUES (?, ?, ?, ?, ?)",
            (employee_id, equipment_id, issued_by, checkout_condition, checkout_time),
        )
        conn.execute(
            "UPDATE equipment SET status = 'Checked Out', condition_name = ? WHERE id = ?",
            (checkout_condition, equipment_id),
        )
        conn.commit()
        checked_out_code = equipment["equipment_code"]
        conn.close()
        flash(f"Equipment {checked_out_code} was successfully checked out to {employee['full_name']}.")
        return redirect(url_for("equipment.employee_profile", employee_id=employee_id))

    conn.close()
    return render_template("equipment/equipment_checkout.html", employee=employee, available_equipment=available_equipment, title="Equipment Checkout")

@equipment_bp.route("/transactions")
def transactions():
    conn = get_connection()
    rows = conn.execute(
        '''
        SELECT t.id, e.full_name, e.employee_id, q.equipment_code, q.equipment_type,
               t.issued_by, t.checkout_condition, t.checkout_time, t.return_time
        FROM checkout_transactions t
        JOIN employees e ON e.id = t.employee_id
        JOIN equipment q ON q.id = t.equipment_id
        ORDER BY t.checkout_time DESC
        '''
    ).fetchall()
    conn.close()
    return render_template("equipment/transactions.html", rows=rows, title="Equipment Transactions")
