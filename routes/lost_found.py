from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from db import get_connection

lost_found_bp = Blueprint("lost_found", __name__, url_prefix="/lost-found")

@lost_found_bp.route("/")
def index():
    return render_template("lost_found/index.html", title="Lost and Found")

@lost_found_bp.route("/items")
def items():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM lost_found_items ORDER BY found_date DESC, id DESC").fetchall()
    conn.close()
    return render_template("lost_found/items.html", rows=rows, title="Lost and Found Items")

@lost_found_bp.route("/claim/<int:item_id>", methods=["GET", "POST"])
def claim_item(item_id):
    conn = get_connection()
    item = conn.execute("SELECT * FROM lost_found_items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        flash("Lost and found item not found.", "error")
        return redirect(url_for("lost_found.items"))
    if request.method == "POST":
        claimed_by = request.form.get("claimed_by", "").strip()
        if not claimed_by:
            conn.close()
            flash("Please enter who is claiming the item.", "error")
            return redirect(url_for("lost_found.claim_item", item_id=item_id))
        if item["status"] == "Claimed":
            conn.close()
            flash("This item has already been claimed.", "error")
            return redirect(url_for("lost_found.items"))
        claimed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "UPDATE lost_found_items SET status = ?, claimed_by = ?, claimed_at = ? WHERE id = ?",
            ("Claimed", claimed_by, claimed_at, item_id),
        )
        conn.commit()
        conn.close()
        flash(f"{item['item_name']} was successfully marked as claimed.")
        return redirect(url_for("lost_found.items"))
    conn.close()
    return render_template("lost_found/claim_item.html", item=item, title="Claim Lost Item")
