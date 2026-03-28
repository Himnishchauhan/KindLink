# 🌍 KindLink - Precision Volunteering & Global Impact

**KindLink** is a next-generation platform designed to bridge the gap between global expertise and local NGO missions. By utilizing intelligent matching and a mobile-first, industrial aesthetic, KindLink empowers volunteers to contribute their specific skills where they are needed most, while providing NGOs with a powerful showcase for their social impact.

---

## 🚀 Key Features

### 💎 Precision Matching
Our platform intelligently analyzes volunteer skills (UI/UX, Data Science, Legal Advocacy, etc.) and matches them with specific NGO opportunities, ensuring maximum synergy and real-world results.

### 🖼️ Public NGO Discovery
A high-impact, publicly accessible gallery where anyone can explore the KindLink network. Visitors can discover organizations, read their mission statements, and explore their "Impact Stories" before even signing up.

### 💳 Seamless Gifting (Razorpay)
Integrated with the **Razorpay Standard Checkout**, KindLink offers a beautiful, "Stay-on-Site" donation experience. Support the community's Impact Fund directly through a secure, branded modal.

### 📱 Industrial Mobile-First Design
Built with a "Midnight Navy" and "Royal Blue" aesthetic, the platform features responsive bento-grid dashboards, ensuring a premium experience on everything from a desktop workstation to a mobile phone.

### 👁️ Enhanced Security UI
User-centric features like the "Show Password" toggle on all authentication screens ensure a smooth and secure experience for every member of the community.

---

## 🛠️ Tech Stack

- **Backend:** Python / Flask
- **Database:** SQLite (with SQLAlchemy ORM)
- **Payments:** Razorpay Python SDK
- **Frontend:** HTML5, Vanilla CSS3 (Industrial Aesthetic)
- **Icons & Type:** FontAwesome 6, Google Fonts (Inter)
- **Environment:** python-dotenv for secure key management

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Himnishchauhan/KindLink.git
cd KindLink
```

### 2. Install Dependencies
Ensure you have Python 3.8+ installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add your Razorpay credentials:
```env
RAZORPAY_KEY_ID=your_rzp_key_id
RAZORPAY_KEY_SECRET=your_rzp_key_secret
```
*(Refer to `razorpay.env.example` for the template)*

### 4. Initialize the Database
If you are starting fresh or need to update the schemaf or Razorpay:
```bash
python migrate_db.py
```

### 5. Seed the Platform (Optional)
To populate the platform with 20 diverse, high-quality Volunteer and NGO profiles:
```bash
python seed_data.py
```
*Note: Default password for seeded accounts is `password123`*

### 6. Run the Application
```bash
python app.py
```
The platform will be available at `http://127.0.0.1:5000`

---

## 🤝 Contributing
We welcome contributions that align with our mission of precision volunteering. Please feel free to submit a Pull Request or open an issue for any UI refinements or feature suggestions.

---

## 📜 License
Created for the **FLUX Hackathon 2026**. Precision giving for social change.
