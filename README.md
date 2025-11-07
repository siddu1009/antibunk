# School Surveillance System

This project is a school surveillance system that uses face recognition to monitor students and enforce rules within a school environment.

## Project Status

The application is currently in a functional state. It can perform the following actions:
- Capture video from a camera source.
- Detect faces in the video stream.
- Recognize known students from a database.
- Apply a set of rules based on student location and time.
- Provide a web-based viewer to display the camera feed with annotations.

## Running the Application

To run the application, you need to start two separate processes in two different terminals from the project's root directory.

### 1. Start the Web Viewer

This component runs a web server that streams the video feed to a web browser.

In your first terminal, run the following command:

```bash
python -m school_surveillance.src.web_viewer
```

### 2. Start the Main Surveillance Application

This is the core component that performs video processing, face recognition, and rule enforcement.

In your second terminal, run the following command:

```bash
python -m school_surveillance.src.main
```

After starting both components, you can view the surveillance feed by opening a web browser and navigating to the address provided by the web viewer (typically `http://127.0.0.1:5000`).
