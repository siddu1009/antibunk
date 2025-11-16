# school_surveillance/src/config.py

DATABASE_NAME = "school_surveillance.db"

# Paths to data configuration files
CAMERA_CONFIG_PATH = "school_surveillance/data/camera_config.json"
SCHEDULES_PATH = "school_surveillance/data/schedules.json"
ZONES_PATH = "school_surveillance/data/zones.json"
STUDENT_IMAGES_DB_PATH = "school_surveillance/data/student_images"

# SMTP Server Settings for Email Notifications
SMTP_HOST = "your_smtp_host"
SMTP_PORT = 587  # or 465 for SSL
SMTP_USERNAME = "your_smtp_username"
SMTP_PASSWORD = "your_smtp_password"
SMTP_SENDER_EMAIL = "your_sender_email@example.com"
