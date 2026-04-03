# 🏏 5A Premier League 2026 — Cricket Scorer App

## Setup Instructions

### 1. Install dependencies
```bash
pip install streamlit Pillow
```

### 2. Folder Structure
```
cricket_app/
├── app.py
├── requirements.txt
├── match_state.json       ← auto-created on first run
└── photos/
    ├── logo_Strikers.jpg
    ├── logo_Knight_Riders.jpg
    ├── logo_Blasters.jpg
    ├── logo_Warriors.jpg
    ├── logo_Challengers.jpg
    └── [PlayerName].jpg   ← one per player (40 total)
```

### 3. Run the app
```bash
cd cricket_app
streamlit run app.py
```

### 4. Projector Setup
- On your laptop: open `http://localhost:8501` in browser
- Connect projector → Extend Display (not Mirror)
- Drag the browser window to projector screen
- App is **self-contained** — no internet needed during match

### 5. How to Score
- Home → Start/Resume Match → Setup (toss, openers, bowler) → Live
- Use **0,1,2,3,4,6** buttons for runs
- Use **W** for wickets → select new batsman
- Use **Wide/No Ball** for extras
- After 4 overs or 8 wickets → Innings 2 setup → Match Result auto-calculated

### 6. Player Photo Files (in photos/ folder)
Replace avatar placeholders with real photos:
- File name = PlayerName with spaces replaced by underscores
- Example: `Prathamesh_Jadhav.jpg`
- Size: 200×200px recommended, JPG format

### Teams & Players
| 5A Strikers | 5A Knight Riders | 5A Blasters | 5A Warriors | 5A Challengers |
|---|---|---|---|---|
| Prathamesh Jadhav | Vaibhav Kamble | Mayur Jadav | Mandar Jadhav | Makrand Jadhav |
| Vaibhav Mohite | Siddhesh Jadhav | Akshay Kamble | Suyash Dhotre | Sushant Gamare |
| Anish Sawant | Harshwardhan Bagade | Umesh Waydande | Aakash Kamble (Matkar) | Shailesh Gopireddy |
| Sumit Kamble | Siddhesh Vadepalli | Ojas Jadav | Prasad Kadam | Sahil Kamble |
| Subodh Padelkar | Yogesh Tambe | Prashant Pawar | Rahul Shinde | Mandar Waydande |
| Nitin Kamble | Aakash Kamble | Prashant Jadhav | Amol Kamble | Shashank Kamble |
| Tanmay Jadhav | Rajendra Dhotre | Sahil Jadhav | Sujal Kamble | Nayan Kamble |
| Sarvesh Sawant | Sandesh Padelkar | Abhishek Mohite | Kaustubh Sawant | Vibhas Kamble |
