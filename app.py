import os
import re

import pymysql
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)


# Load variables from the local .env file.
load_dotenv()


# Create the Flask application.
app = Flask(__name__)


# General application settings.
app.config["SECRET_KEY"] = os.getenv(
    "APP_SECRET_KEY",
    "change-this-key-in-production",
)

DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "Yazen Albu")
APP_PORT = int(os.getenv("APP_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"


# MySQL database settings.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "phonebook_user"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "phonebook_db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
    "connect_timeout": 5,
}


def get_db_connection():
    """Create and return a new MySQL connection."""
    return pymysql.connect(**DB_CONFIG)


def format_person(record):
    """Convert a database record into a display-ready dictionary."""
    return {
        "id": record["id"],
        "name": record["name"].strip().title(),
        "number": record["number"],
    }


def find_persons(keyword):
    """Find phonebook records containing the supplied name."""
    search_value = f"%{keyword.strip().lower()}%"
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, number
                FROM phonebook
                WHERE LOWER(name) LIKE %s
                ORDER BY name;
                """,
                (search_value,),
            )

            records = cursor.fetchall()
            return [format_person(record) for record in records]
    finally:
        connection.close()


def get_person_by_id(person_id):
    """Return one phonebook contact by its database ID."""
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, number
                FROM phonebook
                WHERE id = %s;
                """,
                (person_id,),
            )

            record = cursor.fetchone()

            if record is None:
                return None

            return format_person(record)
    finally:
        connection.close()


def validate_person(name, number):
    """Validate contact form data and return an error message if invalid."""
    if not name:
        return "Please enter the contact name."

    if len(name) > 100:
        return "The contact name cannot exceed 100 characters."

    if not number:
        return "Please enter the phone number."

    if len(number) > 30:
        return "The phone number cannot exceed 30 characters."

    allowed_phone_pattern = r"^[0-9+()\s/-]{5,30}$"

    if not re.fullmatch(allowed_phone_pattern, number):
        return (
            "The phone number may contain only numbers, spaces, "
            "plus signs, brackets, slashes, and hyphens."
        )

    return None


def create_person(name, number):
    """Insert a new person into the phonebook table."""
    normalized_name = name.strip().lower()
    normalized_number = number.strip()

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO phonebook (name, number)
                VALUES (%s, %s);
                """,
                (normalized_name, normalized_number),
            )
    finally:
        connection.close()


def update_person(person_id, name, number):
    """Update an existing phonebook contact."""
    normalized_name = name.strip().lower()
    normalized_number = number.strip()

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE phonebook
                SET name = %s,
                    number = %s
                WHERE id = %s;
                """,
                (
                    normalized_name,
                    normalized_number,
                    person_id,
                ),
            )
    finally:
        connection.close()


def delete_person(person_id):
    """Delete a phonebook contact by its database ID."""
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM phonebook
                WHERE id = %s;
                """,
                (person_id,),
            )

            return cursor.rowcount
    finally:
        connection.close()


@app.route("/", methods=["GET", "POST"])
def home():
    """Display the search page and process search requests."""
    if request.method == "POST":
        keyword = request.form.get("username", "").strip()

        if not keyword:
            return render_template(
                "index.html",
                results=[],
                show_result=False,
                error_message="Please enter a name to search.",
                developer_name=DEVELOPER_NAME,
            )

        try:
            results = find_persons(keyword)
        except pymysql.MySQLError:
            app.logger.exception("Database search failed.")

            return render_template(
                "index.html",
                results=[],
                show_result=False,
                error_message="Could not connect to the phonebook database.",
                developer_name=DEVELOPER_NAME,
            )

        return render_template(
            "index.html",
            results=results,
            searched_keyword=keyword,
            show_result=True,
            error_message=None,
            developer_name=DEVELOPER_NAME,
        )

    return render_template(
        "index.html",
        results=[],
        show_result=False,
        error_message=None,
        developer_name=DEVELOPER_NAME,
    )


@app.route("/add", methods=["GET", "POST"])
def add_contact():
    """Display the add form and create a new phonebook contact."""
    person = {
        "name": "",
        "number": "",
    }

    if request.method == "POST":
        person["name"] = request.form.get("name", "").strip()
        person["number"] = request.form.get("number", "").strip()

        validation_error = validate_person(
            person["name"],
            person["number"],
        )

        if validation_error:
            return render_template(
                "add-update.html",
                page_title="Add Contact",
                button_text="Add Contact",
                person=person,
                error_message=validation_error,
                developer_name=DEVELOPER_NAME,
            ), 400

        try:
            create_person(
                person["name"],
                person["number"],
            )

        except pymysql.err.IntegrityError:
            return render_template(
                "add-update.html",
                page_title="Add Contact",
                button_text="Add Contact",
                person=person,
                error_message="A contact with this name already exists.",
                developer_name=DEVELOPER_NAME,
            ), 409

        except pymysql.MySQLError:
            app.logger.exception("Adding the contact failed.")

            return render_template(
                "add-update.html",
                page_title="Add Contact",
                button_text="Add Contact",
                person=person,
                error_message="The contact could not be added.",
                developer_name=DEVELOPER_NAME,
            ), 500

        flash(
            f"{person['name'].title()} was added successfully.",
            "success",
        )

        return redirect(url_for("home"))

    return render_template(
        "add-update.html",
        page_title="Add Contact",
        button_text="Add Contact",
        person=person,
        error_message=None,
        developer_name=DEVELOPER_NAME,
    )


@app.route("/update/<int:person_id>", methods=["GET", "POST"])
def update_contact(person_id):
    """Display the update form and update an existing contact."""
    try:
        person = get_person_by_id(person_id)
    except pymysql.MySQLError:
        app.logger.exception("Loading the contact failed.")
        abort(500)

    if person is None:
        abort(404)

    if request.method == "POST":
        person["name"] = request.form.get("name", "").strip()
        person["number"] = request.form.get("number", "").strip()

        validation_error = validate_person(
            person["name"],
            person["number"],
        )

        if validation_error:
            return render_template(
                "add-update.html",
                page_title="Update Contact",
                button_text="Save Changes",
                person=person,
                error_message=validation_error,
                developer_name=DEVELOPER_NAME,
            ), 400

        try:
            update_person(
                person_id,
                person["name"],
                person["number"],
            )

        except pymysql.err.IntegrityError:
            return render_template(
                "add-update.html",
                page_title="Update Contact",
                button_text="Save Changes",
                person=person,
                error_message="A contact with this name already exists.",
                developer_name=DEVELOPER_NAME,
            ), 409

        except pymysql.MySQLError:
            app.logger.exception("Updating the contact failed.")

            return render_template(
                "add-update.html",
                page_title="Update Contact",
                button_text="Save Changes",
                person=person,
                error_message="The contact could not be updated.",
                developer_name=DEVELOPER_NAME,
            ), 500

        flash(
            f"{person['name'].title()} was updated successfully.",
            "success",
        )

        return redirect(url_for("home"))

    return render_template(
        "add-update.html",
        page_title="Update Contact",
        button_text="Save Changes",
        person=person,
        error_message=None,
        developer_name=DEVELOPER_NAME,
    )


@app.route("/delete/<int:person_id>", methods=["GET", "POST"])
def delete_contact(person_id):
    """Display a confirmation page and delete a contact."""
    try:
        person = get_person_by_id(person_id)
    except pymysql.MySQLError:
        app.logger.exception("Loading the contact for deletion failed.")
        abort(500)

    if person is None:
        abort(404)

    if request.method == "POST":
        try:
            deleted_rows = delete_person(person_id)
        except pymysql.MySQLError:
            app.logger.exception("Deleting the contact failed.")

            return render_template(
                "delete.html",
                person=person,
                error_message="The contact could not be deleted.",
                developer_name=DEVELOPER_NAME,
            ), 500

        if deleted_rows == 0:
            abort(404)

        flash(
            f"{person['name']} was deleted successfully.",
            "success",
        )

        return redirect(url_for("home"))

    return render_template(
        "delete.html",
        person=person,
        error_message=None,
        developer_name=DEVELOPER_NAME,
    )


@app.route("/health")
def health():
    """Return the application health status."""
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=APP_PORT,
        debug=FLASK_DEBUG,
    )