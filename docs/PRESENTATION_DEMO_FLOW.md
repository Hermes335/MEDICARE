# Presentation Demo Flow

Use this as a 5-7 minute live demo script for MEDIBoT / MediGuide.

## 1. Opening: What the app does

Start with a one-line problem statement:
"People often do not know which medicine to take, whether it is safe, or where to buy it nearby. MEDIBoT helps with symptom-based guidance, pharmacy search, and health tracking in one flow."

Then show the landing or onboarding screen and highlight three things:
- AI-powered medicine guidance
- Nearby pharmacy lookup
- Personal history and saved medicines

## 2. Live demo flow

### Step A: Sign in or register
Show the login screen and quickly authenticate.

Talk track:
- The app keeps user history and saved medicines per account.
- Authentication is built into the same flow, so the user can continue where they left off.

### Step B: Ask for medicine guidance
Go to the chat screen and type a realistic symptom or medicine question.

Good example prompts:
- "I have a mild fever and headache. What can I take?"
- "Is ibuprofen prescription or OTC?"
- "I have a sore throat and cough. What is safe?"

What to highlight:
- The response is structured, not just a plain chat reply.
- It can show medicine name, use case, dosage guidance, warnings, and pharmacy availability.
- It includes safety messaging for prescription drugs and emergencies.

### Step C: Show the safety guardrails
Use a prompt that should trigger caution or escalation.

Example:
- "Chest pain and difficulty breathing"

Talk track:
- The system should avoid giving casual medicine advice for emergencies.
- It escalates with urgent care guidance instead of unsafe recommendations.

### Step D: Show nearby pharmacy lookup
Switch to the pharmacy screen and search for nearby pharmacies.

What to highlight:
- The app uses location-aware pharmacy lookup.
- Results are shown on a real map with markers and distance sorting.
- This makes the recommendation actionable, not just informational.

### Step E: Show history and saved medicines
Open the history screen.

Talk track:
- Previous interactions are stored for follow-up questions.
- Saved medicines help users revisit important recommendations.
- This makes the app useful beyond a single chat session.

## 3. Close with the system story

End with a short summary:
"MEDIBoT combines a medical assistant, safety guardrails, pharmacy discovery, and patient memory into one workflow. The goal is not just to answer questions, but to guide users toward the next safe action."

## 4. Suggested demo order for a smooth presentation

1. Open onboarding or landing screen
2. Log in
3. Ask a symptom-based question
4. Show a safety-sensitive example
5. Open pharmacy search
6. Open history and saved meds
7. Close with the value statement

## 5. Backup plan if a service fails

If the live API is unavailable, narrate the flow using screenshots or a previously captured run:
- Frontend loads on port 5173
- Auth and saved data are handled by the Node API on port 3001
- Medical guidance comes from the Flask model service on port 5000

If time is short, skip history and focus on the chat answer plus pharmacy map. That gives the strongest end-to-end story in under 3 minutes.