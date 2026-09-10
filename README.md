1.PORJECT INFORMATION: \
PROJECT TITLE: NagarDrishti-Turning Public Buses into AI-Powered Eyes of the City\
PS ID: SIH26124  \
PS TITLE:AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet\
CATEGORY:Software\
THEME:Smart Automation\
2.PROBLEM STATEMENT:\
Potholes, waterlogging, damaged infrastructure & road hazards →  often addressed only after they become severe or are reported → poor managament and no future predictions
Fixed CCTV & manual inspections → limited, static & intermittent coverage →  roads gets unmonitored
Existing monitoring largely identifies what has already happened, rather than forecasting → no Predictive Risk Intelligence
Absence of automated prioritization and authority routing can delay intervention & waste maintenance resources.
After an issue is reported as resolved →  limited automated verification → no continuous accountability loop
3.PROPOSED SOLUTION:\
Our platform turns ordinary public buses into a city-wide network of AI-powered mobile sensors. As buses move through the city, edge AI analyses their camera feeds to detect potholes, damaged infrastructure, traffic anomalies, waterlogging, and safety events in real time. These observations are fused with CCTV, inspection, historical, and contextual data on a centralized GIS-based intelligence layer, where incidents are cross-validated across multiple buses, assigned dynamic risk scores, and automatically routed to the responsible authority.
Beyond simply detecting problems, the system creates a closed-loop urban response: once an issue is reported and repaired, subsequent buses passing through the same location allow AI to repeatedly verify the repair. Multiple independent verification passes confirm that the issue has been successfully resolved before it is closed, with the outcome fed back into the system for continuous learning.
Detect → Assess → Act → Verify → Learn — transforming public transport from a means of mobility into an intelligent, continuously learning urban sensing network.
4.KEY FEATURES:\
 * Fleet-as-a-Sensor Network public buses → mobile urban sensors (no separate survey vehicles)
 * Multi-Bus Evidence Fusion Repeated detections → verified issue reduced false positives & duplicate report
 * Predictive Urban Intelligence Road deterioration detected → trend analyzed → condition predicted
 * Closed-Loop Repair Verification subsequent bus passes the location & AI checks Detect → Act → Verify → Learn
5:TECHNOLOGY STACK:\
FRONTEND:React.js,Tailwind CSS,Javascript
DATABASE:PostgreSQL
BACKEND:FastAPI,Python,Unicorn
MACHINE LEARNING:Python, YOLO, PyTorch, OpenCV
ALERTS:Firebase Cloud Messaging
CLOUD AND DEPLOYMENT:AWS
6.ARCHITECTURE:\

7.FUTURE SCOPE:\
*Modular AI architecture → new detection models to be added independently.
*Edge + cloud architecture → buses process video locally while the central platform stores only relevant events and metadata → prevents cloud from becoming a bottleneck as fleet grows.
*GIS-based jurisdiction layer →automatically map incidents to concerned departments & authorities as deployment expands.
*lightweight AI models to run on different edge devices as onboard computing capabilities evolve.
