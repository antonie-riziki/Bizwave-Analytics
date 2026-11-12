# Biz Backend

A Django REST API for the Biz platform. The backend provides token-authenticated account endpoints and owner-scoped business management endpoints, with PostgreSQL as the local development database.

This guide is written for **Git Bash on Windows**. It follows the complete setup path from cloning the repository to verifying the database, API, and Git state.

## What This Project Uses

- Python 3.14 or compatible Python version
- Django 6.1.3
- Django REST Framework
- Token authentication
- PostgreSQL 18
- `django-cors-headers`
- `python-dotenv`
- scikit-learn, pandas, NumPy, and supporting data packages

## Project Layout

```text
biz/
|-- backend/
|   |-- manage.py
|   |-- requirements.txt
|   |-- .env                 # local only; ignored by Git
|   |-- config/               # Django project settings and URLs
|   |-- accounts/             # registration, login, logout, current user
|   |-- businesses/           # authenticated business CRUD API
|   |-- analytics/
|   |-- communications/
|   |-- engagement/
|   |-- ingestion/
|   `-- integrations/
`-- README.md
```

## Prerequisites

Install these before starting:

1. Git for Windows with Git Bash
2. Python with `python` available in Git Bash
3. PostgreSQL for Windows
4. A PostgreSQL administrator password created during PostgreSQL installation

Check the first two tools:

```bash
git --version
python --version
```

Check the PostgreSQL 18 client installed by the Windows installer:

```bash
"/c/Program Files/PostgreSQL/18/bin/psql.exe" --version
```

If PostgreSQL is installed in another version directory, update that path in the commands below.

## Clone or Open the Repository

For a new checkout:

```bash
cd /c/Users/Admin/code
git clone <YOUR_REPOSITORY_URL> biz
cd biz
```

For an existing checkout:

```bash
cd /c/Users/Admin/code/biz
git status
```

The remainder of this guide assumes the repository is located at:

```text
C:/Users/Admin/code/biz
```

## Create the Python Environment

Move into the backend:

```bash
cd /c/Users/Admin/code/biz/backend
```

Create a virtual environment once:

```bash
python -m venv .venv
```

Activate it in every new Git Bash terminal:

```bash
source .venv/Scripts/activate
```

After activation, the prompt should contain `(.venv)`. Confirm that Git Bash is using the virtual environment:

```bash
which python
python --version
python -m pip --version
```

The Python path should contain:

```text
/c/Users/Admin/code/biz/backend/.venv/Scripts/python
```

## Install Python Dependencies

Upgrade packaging tools, then install the exact versions recorded by the project:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Confirm the important packages are available:

```bash
python -c "import django, rest_framework, corsheaders, psycopg; print('Django', django.get_version()); print('dependencies ok')"
```

## Start PostgreSQL on Windows

The project expects PostgreSQL at `127.0.0.1:5432`.

Check whether the PostgreSQL 18 Windows service is running:

```bash
powershell.exe -NoProfile -Command "Get-Service postgresql-x64-18 | Select-Object Name,Status"
```

If it is stopped, start it from an **Administrator Git Bash** window:

```bash
net start postgresql-x64-18
```

If your installed service has a different name, list PostgreSQL services:

```bash
powershell.exe -NoProfile -Command "Get-Service *postgres* | Select-Object Name,Status,DisplayName"
```

Confirm that PostgreSQL is listening on port 5432:

```bash
powershell.exe -NoProfile -Command "Get-NetTCPConnection -LocalPort 5432 -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess"
```

## Create the PostgreSQL Role and Database

The Django settings read these variables from `backend/.env`:

```text
DB_NAME=sme_platform
DB_USER=sme_admin
DB_PASSWORD=<your-local-password>
DB_HOST=127.0.0.1
DB_PORT=5432
```

Open PostgreSQL as the administrator. The command will ask for the PostgreSQL administrator password:

```bash
"/c/Program Files/PostgreSQL/18/bin/psql.exe" -h 127.0.0.1 -U postgres -d postgres
```

Inside the `psql` prompt, create the application role and database:

```sql
CREATE ROLE sme_admin LOGIN PASSWORD '<your-local-password>';
CREATE DATABASE sme_platform OWNER sme_admin;
GRANT ALL PRIVILEGES ON DATABASE sme_platform TO sme_admin;
\q
```

If PostgreSQL says that the role or database already exists, do not create it again. Connect as `postgres` and use the existing objects instead:

```sql
ALTER ROLE sme_admin WITH LOGIN PASSWORD '<your-local-password>';
ALTER DATABASE sme_platform OWNER TO sme_admin;
\q
```

Test the application credentials directly. Replace the password when prompted:

```bash
"/c/Program Files/PostgreSQL/18/bin/psql.exe" -h 127.0.0.1 -U sme_admin -d sme_platform -c "SELECT current_user, current_database();"
```

Expected output includes:

```text
 current_user | current_database
--------------+-----------------
 sme_admin    | sme_platform
```

### PostgreSQL Authentication Troubleshooting

If you see:

```text
FATAL: password authentication failed for user "sme_admin"
```

verify all of the following:

```bash
"/c/Program Files/PostgreSQL/18/bin/psql.exe" -h 127.0.0.1 -U sme_admin -d sme_platform -c "SELECT 1;"
```

- PostgreSQL is running.
- The database name is `sme_platform`.
- The role name is `sme_admin`.
- The password matches both PostgreSQL and `.env`.
- The port is `5432`.

To reset the application role password, connect as `postgres` and run:

```sql
ALTER ROLE sme_admin WITH LOGIN PASSWORD '<your-local-password>';
\q
```

Do not change `pg_hba.conf` to `trust` for normal development. Password authentication is the correct local configuration for this project.

## Create the Environment File

From `backend/`, create a local `.env` file. This file is ignored by Git and must never be committed:

```bash
cd /c/Users/Admin/code/biz/backend
cat > .env <<'EOF'
DB_NAME=sme_platform
DB_USER=sme_admin
DB_PASSWORD=<your-local-password>
DB_HOST=127.0.0.1
DB_PORT=5432
EOF
```

Replace `<your-local-password>` with the same password assigned to the PostgreSQL role. Do not include angle brackets in the real value.

Confirm that the file exists without printing its secret:

```bash
test -f .env && echo ".env exists"
grep -E '^(DB_NAME|DB_USER|DB_HOST|DB_PORT)=' .env
```

Do not run `cat .env` in a shared terminal because it prints the database password.

## Verify Django Can Load the Configuration

Run the system check:

```bash
cd /c/Users/Admin/code/biz/backend
source .venv/Scripts/activate
python manage.py check
```

Expected:

```text
System check identified no issues (0 silenced).
```

Test the database connection through Django:

```bash
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('database connection ok')"
```

## Create and Apply Migrations

Check whether model changes need migration files:

```bash
python manage.py makemigrations --check --dry-run
```

Expected when everything is synchronized:

```text
No changes detected
```

Review pending migration operations:

```bash
python manage.py migrate --plan
```

Apply all migrations:

```bash
python manage.py migrate --noinput
```

Expected when the database is current:

```text
No migrations to apply.
```

Display the final migration state:

```bash
python manage.py showmigrations --plan
```

Every applied migration should have `[X]` beside it.

## Create an Administrator

Create a Django admin account interactively:

```bash
python manage.py createsuperuser
```

Follow the prompts for username, email, and password. Open the admin site after starting the server:

```text
http://127.0.0.1:8000/admin/
```

## Run the Backend

Start the development server from `backend/`:

```bash
cd /c/Users/Admin/code/biz/backend
source .venv/Scripts/activate
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

Keep this terminal open. Stop the server with `CTRL+C`.

The project currently exposes:

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | Public | Create an account and token |
| POST | `/api/auth/login/` | Public | Authenticate and receive a token |
| POST | `/api/auth/logout/` | Token | Delete the current token |
| GET | `/api/auth/me/` | Token | Return the current user |
| GET | `/api/businesses/` | Token | List the current user's businesses |
| POST | `/api/businesses/` | Token | Create a business owned by the current user |
| GET | `/api/businesses/<id>/` | Token | Retrieve an owned business |
| PUT/PATCH | `/api/businesses/<id>/` | Token | Update an owned business |
| DELETE | `/api/businesses/<id>/` | Token | Delete an owned business |
| GET | `/admin/` | Admin | Open Django admin |

There is no homepage route, so `GET /` returning `404` is expected. Use the API or admin URLs above.

## Run the Automated Checks

Use a second Git Bash terminal while the server is running:

```bash
cd /c/Users/Admin/code/biz/backend
source .venv/Scripts/activate
```

Run the configuration check:

```bash
python manage.py check
```

Check migrations:

```bash
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan
```

Run the test suite:

```bash
python manage.py test
```

A successful command exits with status `0`. If the test output says `Ran 0 tests`, the command itself passed but the project does not yet contain automated test cases.

## Test the Live API with Git Bash

These commands use `curl`, not PowerShell syntax.

### Register

Create a unique test email:

```bash
EMAIL="check-$(date +%s)@example.com"
PASSWORD='CheckPassword2026!'
```

Register:

```bash
curl -i -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d "{\"first_name\":\"Git\",\"last_name\":\"Check\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}"
```

Expected status:

```text
HTTP/1.1 201 Created
```

### Login and Capture the Token

```bash
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "$LOGIN_RESPONSE"
```

Extract the token using Python, which is already installed in the virtual environment:

```bash
TOKEN=$(printf '%s' "$LOGIN_RESPONSE" | python -c "import json, sys; print(json.load(sys.stdin)['token'])")
echo "token received: ${#TOKEN} characters"
```

### Check the Current User

```bash
curl -i http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Token $TOKEN"
```

Expected status:

```text
HTTP/1.1 200 OK
```

### Create a Business

```bash
curl -i -X POST http://127.0.0.1:8000/api/businesses/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Token $TOKEN" \
  -d '{"name":"Git Check Business","industry":"Testing","country":"Kenya","currency":"KES"}'
```

Expected status:

```text
HTTP/1.1 201 Created
```

### List Businesses

```bash
curl -i http://127.0.0.1:8000/api/businesses/ \
  -H "Authorization: Token $TOKEN"
```

Expected status:

```text
HTTP/1.1 200 OK
```

### Confirm Authentication Is Required

```bash
curl -i http://127.0.0.1:8000/api/auth/me/
```

Expected status:

```text
HTTP/1.1 401 Unauthorized
```

### Log Out

```bash
curl -i -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Authorization: Token $TOKEN"
```

Expected status:

```text
HTTP/1.1 200 OK
```

The token should no longer authenticate requests after logout.

### Remove Smoke-Test Data

The test account and its business can be removed with:

```bash
python manage.py shell -c "from django.contrib.auth.models import User; deleted, _ = User.objects.filter(email__startswith='check-').delete(); print(f'deleted {deleted} object(s)')"
```

Only run this cleanup command if the test account uses the `check-` email prefix.

## Git Health Checks

Run these from the repository root:

```bash
cd /c/Users/Admin/code/biz

git status -sb
git diff --check
git diff --cached --check
git diff --stat
git log -1 --oneline
git branch -vv
git remote -v
git fetch --prune
git status
```

Test authentication to the configured remote without pushing changes:

```bash
git push --dry-run
```

A clean working tree reports:

```text
nothing to commit, working tree clean
```

Local `.env` and `.venv` files should not appear in `git status`. Before committing, inspect exactly what will be included:

```bash
git status --short
git diff --stat
```

Commit and push only after reviewing the diff:

```bash
git add README.md backend
git diff --cached --check
git commit -m "Document backend setup and verification"
git push
```

## Common Problems

### `python: command not found`

Install Python, reopen Git Bash, and confirm:

```bash
python --version
which python
```

### Django says it cannot import a package

Activate the virtual environment and reinstall dependencies:

```bash
cd /c/Users/Admin/code/biz/backend
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

### `connection refused` on port 5432

PostgreSQL is not running or is listening on another port:

```bash
powershell.exe -NoProfile -Command "Get-Service *postgres* | Select-Object Name,Status"
powershell.exe -NoProfile -Command "Get-NetTCPConnection -LocalPort 5432 -State Listen"
```

### `password authentication failed`

The PostgreSQL role password and `.env` password differ. Reset the role as `postgres`:

```sql
ALTER ROLE sme_admin WITH LOGIN PASSWORD '<your-local-password>';
```

Then update `backend/.env` to the same value and retry:

```bash
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('database connection ok')"
```

### `role "sme_admin" does not exist`

Create it as the PostgreSQL administrator:

```sql
CREATE ROLE sme_admin LOGIN PASSWORD '<your-local-password>';
CREATE DATABASE sme_platform OWNER sme_admin;
```

### `No migrations to apply` is not shown

Run:

```bash
python manage.py showmigrations --plan
python manage.py migrate --noinput
```

### `GET /` returns `404`

That is expected because the project currently has no root homepage route. Test one of these instead:

```text
http://127.0.0.1:8000/admin/
http://127.0.0.1:8000/api/auth/register/
http://127.0.0.1:8000/api/businesses/
```

### Git Bash returns exit code 127

Exit code `127` means the shell could not find a command. Do not paste PowerShell commands into Git Bash. Use:

```bash
source .venv/Scripts/activate
python manage.py check
```

Use Git Bash line continuation `\`, not PowerShell backticks.

## Definition of Done

The local backend is ready when all of these are true:

- `python manage.py check` passes.
- `python manage.py makemigrations --check --dry-run` prints `No changes detected`.
- `python manage.py migrate --plan` shows no planned operations.
- `python manage.py test` exits successfully.
- PostgreSQL accepts the `sme_admin` connection.
- Registration returns `201 Created`.
- Login returns a token.
- `/api/auth/me/` returns `200 OK` with that token.
- Business creation returns `201 Created` with that token.
- Anonymous requests to protected endpoints return `401 Unauthorized`.
- `git diff --check` reports no whitespace errors.
- `.env` does not appear in Git status.

## Security Notes

- Never commit `.env`, database passwords, API tokens, or production secrets.
- Replace the development `SECRET_KEY` before production deployment.
- Set `DEBUG = False` in production.
- Configure production `ALLOWED_HOSTS`, CORS origins, CSRF trusted origins, HTTPS, and secure cookies before deployment.
- Do not use PostgreSQL `trust` authentication except as a controlled emergency recovery step, and restore secure password authentication immediately.
- The commands in this README are for local development and verification, not production deployment.
