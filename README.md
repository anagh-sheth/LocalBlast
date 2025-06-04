# 🌍 LocalBlast

LocalBlast is a Django-based SaaS application that helps local businesses improve their visibility on Google Maps by simulating Google Business Profile audits and generating actionable SEO checklists.

---

## 🚀 Features

- 🔐 User authentication (signup, login, logout)
- 🧾 Business profile creation (name, address, category, etc.)
- 📊 Audit engine that simulates a local SEO score
- ✅ Personalized checklist with 5–7 action items based on audit results
- 📈 Dashboard to view progress and re-run audits
- 💳 Stripe integration for Pro plan upgrades
- 🗃️ Admin dashboard (via Django admin)
- ☁️ Serverless PostgreSQL via [Neon](https://neon.tech)
- 🎨 Clean UI with Tailwind CSS

---

## 🧰 Tech Stack

- **Backend:** Django (Python)
- **Frontend:** Django Templates + Tailwind CSS
- **Database:** Neon PostgreSQL (serverless)
- **Payments:** Stripe Checkout
- **Deployment-ready** with `.env` configuration

---

## 🛠️ Setup Instructions

```bash
# 1. Clone the repo:
git clone https://github.com/your-username/localrankfix.git
cd localrankfix

# 2. Create virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# 3. Install dependencies:
pip install -r requirements.txt

# 4. Configure environment variables:
# Create a `.env` file and add the following keys:
# (Don't include the '#' characters in your file)

SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=your-neon-db-url
STRIPE_PUBLIC_KEY=your-stripe-pk
STRIPE_SECRET_KEY=your-stripe-sk
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-key

# 5. Apply migrations:
python manage.py migrate

# 6. Run the development server:
python manage.py runserver
```

---

## 🧪 Demo (Optional)

[Coming Soon]

---

## 💡 Future Features (Planned)

- Competitor comparison data
- Scheduled weekly audits with Celery
- Custom domain support
- Public audit sharing links
- AI-generated suggestions

---

## 📝 License

MIT License. Feel free to fork, remix, or build on it — just give credit!

---

## 📬 Contact

Built by Anagh Sheth
Email: anagh.sheth@gmail.com
