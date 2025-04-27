# 🎬 IMDb Commitment Issues

A full-stack movie web app where users can browse, search, filter, favorite, and manage a watchlist of movies.

Hosted on **AWS EC2** with **AWS RDS (MySQL)** and **Redis** caching.

---

## 🌎 Technologies Used

- **Next.js** (Frontend)
- **Flask** (Backend)
- **MySQL (AWS RDS)** (Database)
- **Redis** (Caching)
- **Docker** (Optional Deployment)
- **AWS EC2** (Hosting)

---

## 🚀 Full Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ECE3824-Spring2025/imdb-commitment-issues.git
cd imdb-commitment-issues
```

---

### 2. Running Locally (Developer Mode)

#### a. Setup Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### b. Install Python and Node.js Dependencies

```bash
pip install -r requirements.txt
npm install
```

#### c. Install and Start Redis Server

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

Check if Redis is running:

```bash
redis-cli ping
# Should return: PONG
```

#### d. Populate the Database (Optional)

```bash
python3 src/scripts/filter_data.py
```

Only run if you want to load initial movie data into the database.

#### e. Start the Web Application

```bash
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:5001/api

---

### 3. Running on AWS EC2 (Elastic IP)

#### a. SSH into your EC2 Instance

```bash
ssh -i /path/to/your-key.pem ubuntu@<your-elastic-ip>
```

#### b. Setup Server Environment

```bash
git clone https://github.com/ECE3824-Spring2025/imdb-commitment-issues.git
cd imdb-commitment-issues

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
npm install

sudo apt install redis-server
sudo systemctl start redis-server
```

#### c. Update `.env` File

Make sure you create or edit your `.env` file in the project root:

```env
NEXT_PUBLIC_API_URL=http://<your-elastic-ip>:5001
REACT_APP_API_BASE_URL=http://<your-elastic-ip>:5001/api

TMDB_API_KEY=<your-tmdb-api-key>
DATABASE_URL=mysql+pymysql://<db-username>:<db-password>@<rds-endpoint>:3306/<db-name>
```

---

### 4. Running with Docker (Optional)

#### a. Install Docker and Docker Compose

```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

#### b. Install Docker Python Requirements

```bash
pip install -r requirements-docker.txt
```

#### c. Build and Run Docker Containers

```bash
docker-compose up --build
```

- Frontend (Next.js) will be served at http://<your-elastic-ip>:3000
- Backend (Flask API) will be served at http://<your-elastic-ip>:5001/api

---

## 📄 Environment Variables

Example `.env` file:

```env
NEXT_PUBLIC_API_URL=http://<your-elastic-ip>:5001
REACT_APP_API_BASE_URL=http://<your-elastic-ip>:5001/api

TMDB_API_KEY=<your-tmdb-api-key>
DATABASE_URL=mysql+pymysql://<db-username>:<db-password>@<rds-endpoint>:3306/<db-name>
```

---

## 🛠️ Website Basic Usage

1. **Sign Up** or **Sign In** first.
2. **Browse** the top 100 movies.
3. **Filter** movies by genre.
4. **Sort** by Most Popular, Top Rated, or Favorites.
5. **Favorite** movies to your personal watchlist.
6. **Search** for movies by title.

---

## 🛟 Troubleshooting

| Problem | Fix |
|:--------|:----|
| "Failed to fetch movies" | Ensure backend is running on port 5001 |
| "Permission denied (publickey)" | Run `chmod 400 your-key.pem` before SSH |
| "Redis not running" | Start it: `sudo systemctl start redis-server` |
| "Database connection error" | Verify RDS settings and security group rules |
| "CORS error" | Make sure Flask CORS setup is correct |

---

## 📜 Quick Commands Summary

```bash
# Clone repo
git clone https://github.com/ECE3824-Spring2025/imdb-commitment-issues.git
cd imdb-commitment-issues

# Setup environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
npm install

# Start Redis
sudo apt install redis-server
sudo systemctl start redis-server

# (Optional) Populate database
python3 src/scripts/filter_data.py

# Run app
npm run dev
```

Or with Docker:

```bash
pip install -r requirements-docker.txt
docker-compose up --build
```

---

