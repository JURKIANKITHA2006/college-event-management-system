import sqlite3

DATABASE = "events.db"

events = [
    ("Guest Lecture on International Day Against Drug Abuse and Illicit Trafficking", "2026-06-27", "Seminar Hall 1"),
    ("Meet your batch mates", "2026-06-27", "R.A Auditorium"),
    ("Subject Lecture on Applied Heat and Mass Transfer in Engineering", "2026-06-26", "Department Smart Class Room"),
    ("ISR on Health Checkup Camp", "2026-06-26", "Thiruverkadu Public Health Centre"),
    ("Competition on National Vitiligo Day", "2026-06-25", "Demonstration Room"),
    ("Interdisciplinary Lecture on Climate Change & Sustainable Lifestyle", "2026-06-25", "E&S Campus"),
    ("Competition on International Day Against Drug Abuse and Illicit Trafficking", "2026-06-24", "PG Hall"),
    ("CPE on Post-Mastectomy Care: From Surgery to Recovery", "2026-06-24", "Basement Auditorium"),
    ("National Day Celebration on PTSD Awareness Day", "2026-06-24", "Smart Room"),
    ("Celebration on Food Fest - On account of President's Birthday", "2026-06-24", "R.A Auditorium"),
    ("Two Days Hands on Training on Hydra Biology and Marine Derivatives", "2026-06-24", "AKC"),
    ("Celebration on International Yoga Day", "2026-06-22", "Seminar Hall 1"),
    ("Celebration on President's Trophy", "2026-06-22", "Main Campus"),
    ("National Yoga Day Celebration in association with Dept of Physiology", "2026-06-21", "University Campus"),
    ("Expert Talk on International Day of Yoga", "2026-06-19", "PG Hall"),
    ("Reward Ceremony on Annual Day", "2026-06-19", "R.A Auditorium"),
    ("CME on Butterfly in Balance: A CME on Thyroid Health", "2026-06-19", "2nd Floor Lecture Theatre"),
    ("Competition on International Day Against Drug Abuse and Illicit Trafficking", "2026-06-19", "Conference Hall"),
    ("Guest Lecture on Blockchain & Its Applications in Commerce", "2026-06-18", "E&S Campus"),
    ("Guest Lecture on Finite Element Analysis in Engineering", "2026-06-18", "Civil Smart Class Room"),
    ("International Conference on Recent Advances and Emerging Developments", "2026-06-17", "R.A Block Auditorium"),
    ("Workshop on Schrodinger Suite (CADD)", "2026-06-17", "Faculty of Pharmacy"),
    ("FDP on AI in Dental Health", "2026-06-16", "TMDCH Auditorium"),
    ("CME on International Yoga Day", "2026-06-16", "Lecture Hall"),
    ("ISR on World Blood Donor Day", "2026-06-16", "RSRM Hospital"),
    ("Competition on World Blood Donor Day", "2026-06-15", "Conference Hall"),
    ("International Webinar on Next-Gen AI: Shaping the Future of Intelligence", "2026-06-15", "Online"),
    ("Expert Talk on Impact of Donors, Community and Solidarity", "2026-06-15", "PG Hall"),
    ("Subject Lecture on CSM Periodontics", "2026-06-15", "TMDCH Auditorium"),
    ("Guest Lecture on Data Science Career Path", "2026-06-14", "R.A Auditorium"),
    ("Interdisciplinary Lecture on Innovations for Modern Healthcare", "2026-06-14", "R.A Auditorium"),
    ("Guest Lecture on Cross-Disciplinary Innovation and Product Development", "2026-06-13", "HMCT Banquet Hall"),
    ("Competition on World Environment Day", "2026-06-13", "Conference Hall"),
    ("Workshop on From AI Tools to Publication: A Practical Journey", "2026-06-12", "Lecture Hall-2, ACS Medical College"),
    ("Workshop on Biochemistry Analyzer", "2026-06-12", "Laboratory"),
    ("CME on Good Clinical Practice", "2026-06-12", "Lecture Hall"),
    ("Competition on World No Tobacco Day", "2026-06-11", "Conference Hall"),
    ("Technology Talk on Research Lecture Series-14", "2026-06-11", "Adayalampattu Campus"),
    ("Guest Lecture on The Psychology of Taste: Sensory Branding in Food", "2026-06-10", "HMCT Banquet Hall"),
    ("Subject Lecture on CVSL Regulation Endurance in Stroke", "2026-06-10", "2nd Floor Lecture Theatre"),
    ("Inter Disciplinary Lecture on World Brain Tumor Day", "2026-06-10", "Conference Hall"),
    ("Inauguration of Journal Club / Student Chapter / LAB", "2026-06-09", "AHS Auditorium"),
    ("Three Days FDP on Task-Based Teaching of LSRW Skills", "2026-06-09", "Civil Smart Room"),
    ("FDP on MOOC Development", "2026-06-08", "Online"),
    ("Competition (Quiz) on World Brain Tumor Day 2026", "2026-06-08", "Lecture Hall-129"),
    ("CME on Recent Advancements in Imaging", "2026-06-07", "AHS Auditorium"),
    ("Guest Lecture on Behavioral Finance: The Psychology of Investment", "2026-06-07", "Online"),
    ("Competition on World Environment Day", "2026-06-06", "PG Hall"),
    ("Competition on World Environment Day", "2026-06-06", "Online"),
    ("National Day Event on World Environment Day", "2026-06-05", "R.A Auditorium"),
    ("National Day Celebration on World Environment Day", "2026-06-05", "Smart Room"),
    ("Conclave on Quality Assurance in Learning", "2026-06-05", "University Auditorium"),
    ("ISR Event on World Environmental Day in association with NSS", "2026-06-05", "Outside Campus"),
    ("ISR Event on World No Tobacco Day", "2026-05-31", "Outside"),
    ("Interdisciplinary Lecture on Electronic Data Acquisition Systems", "2026-05-31", "R.A Block Auditorium"),
    ("Guest Lecture on Advanced Techniques in Cardiology", "2026-05-30", "Lecture Hall-328"),
    ("Online Seminar on Real Life Application in Calculus", "2026-05-30", "Google Meet"),
    ("Subject Lecture on Battery Management Systems for Electric Vehicles", "2026-05-29", "VERA Block Auditorium"),
    ("ISR Event on World No Tobacco Day", "2026-05-29", "Outside Campus"),
    ("Competition on Anti-Tobacco Day", "2026-05-28", "Online"),
    ("ISR Event on Drug Awareness", "2026-05-28", "Outside Campus"),
    ("Industrial Training on Industrial Workshop", "2026-05-27", "Offline - Industry"),
    ("Alumni Lecture Series-28 on Beyond Technical Skills", "2026-05-27", "University Auditorium"),
    ("Subject Lecture on Client-Side Web Design Technologies", "2026-05-26", "R.A Auditorium"),
    ("Celebration on Valedictory Ceremony of IEI INNOVISTA-2026", "2026-05-26", "R.A Auditorium"),
    ("Certificate Training Program", "2026-05-25", "Sun Java Lab"),
    ("Subject Lecture on Foundations of Data Computing", "2026-05-25", "R.A Auditorium"),
    ("Technology Talk on Smart Grids: Architecture, Operation & Challenges", "2026-05-24", "R.A Block Auditorium"),
    ("Alumni Interaction Series XVIII on Roadmaps to Success", "2026-05-24", "R.A Auditorium"),
    ("Technical Talk on Digital Mental Health & Tele-Counseling", "2026-05-23", "Online"),
    ("Seminar on ICT Tools (Series-14)", "2026-05-23", "Smart Room"),
    ("Workshop on Hematology Analyzer", "2026-05-22", "BioInformatics Lab"),
    ("Inter-Department Technical Talk on Data Analysis for Mechanical Engineering", "2026-05-21", "Department Smart Class Room"),
    ("Inter Disciplinary Lecture on Culinary Nutrition: The Science of Wellness", "2026-05-21", "IHMCT Banquet Hall"),
    ("Alumni Interaction on Innovation-Driven Careers, Start-ups and Innovation", "2026-05-20", "AKC"),
    ("FDP on Effective Assessment & Evaluation Techniques", "2026-05-20", "Online"),
    ("ISR on Updates on HIV Vaccine", "2026-05-19", "RSRM Hospital"),
    ("Inter-Disciplinary Lecture on World Telecommunication Day", "2026-05-17", "2nd Floor Lecture Theatre"),
    ("International Day of Yoga", "2026-05-16", "R.A Auditorium"),
    ("Interdisciplinary Lecture on The Dark Side of Digital: E-Waste & Recycling", "2026-05-15", "Online"),
]

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

for name, date, venue in events:
    cursor.execute(
        """
        INSERT INTO events
        (name, date, time, venue, description, registration_deadline, registration_open)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            date,
            "10:00 AM",
            venue,
            "College Event",
            date,
            1
        )
    )

conn.commit()
conn.close()

print(f"{len(events)} events added successfully!")