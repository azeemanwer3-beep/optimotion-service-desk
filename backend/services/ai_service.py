"""
AI Service — Gemini integration for EV troubleshooting.

Features:
  - Streaming responses for real-time chat UX
  - Issue categorization
  - Ticket summary generation
  - Mock mode when no API key is configured (for demos)
"""

import os
import json
import time
from typing import Generator
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ─── Prompts ──────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert EV (Electric Vehicle) troubleshooting assistant for Optimotion, an EV rental company. Your role is to help customers resolve issues with their rented electric vehicles quickly and effectively.

## Your Behavior:
1. **Acknowledge** the customer's frustration empathetically
2. **Diagnose** by asking targeted clarifying questions if needed
3. **Provide** clear, numbered step-by-step troubleshooting instructions
4. **Explain** why each step works (briefly)
5. Be concise, professional, and reassuring

## Common EV Issues & Solutions:

### Vehicle Won't Start
- Check if key fob battery is low (dashboard shows key icon)
- Ensure brake pedal is firmly pressed while pressing START
- Check if vehicle is in PARK
- Try: Hold START button for 5 seconds with key fob on center console

### Charging Issues
- Verify charging cable is firmly connected at both ends
- Check charging port light (green = charging, red = error)
- Try a different station/outlet
- Reset: unplug, wait 30 seconds, reconnect

### Battery/Range Concerns
- Eco mode extends range by 15-20%
- Reduce climate control intensity
- Check tire pressure (low pressure = reduced range)
- Avoid rapid acceleration

### App Connectivity Issues
- Toggle Bluetooth on/off
- Toggle airplane mode on/off
- Log out and back into the Optimotion app
- Check app permissions (location, Bluetooth, notifications)

### Dashboard Warnings
- Tire pressure: inflate to recommended PSI (driver door jamb)
- Battery temperature: park in shade, avoid fast charging
- Service light: note warning, may need appointment

### Infotainment/Display Issues
- Soft reset: hold power button 10 seconds
- Hard reset: hold both scroll wheels 10 seconds
- Check screen brightness

## Response Format:
- Use markdown formatting for clarity
- Number your troubleshooting steps
- Use **bold** for important actions
- Keep responses focused and actionable
- If safety concern (smoke, unusual sounds): recommend emergency support immediately

## Important:
- Never provide information you're unsure about
- If troubleshooting won't solve the issue, clearly state a service appointment is needed
- Always prioritize customer safety"""


TICKET_SUMMARY_PROMPT = """Based on the following conversation between a customer and the troubleshooting assistant, generate a structured service ticket summary.

Return a JSON object with these fields:
- "title": A concise title for the service ticket (max 100 chars)
- "description": A detailed description of the issue and what was tried
- "category": One of: "battery", "charging", "starting", "app", "infotainment", "tire", "safety", "other"
- "priority": One of: "low", "medium", "high", "critical" (based on severity and safety impact)
- "ai_summary": A brief summary of the troubleshooting steps attempted and why they didn't resolve the issue

Conversation:
{conversation}

Return ONLY the JSON object, no other text."""


CATEGORY_PROMPT = """Based on this issue description, categorize it into exactly one of these categories:
battery, charging, starting, app, infotainment, tire, safety, other

Issue: {issue}

Return ONLY the category name, nothing else."""


# ─── AI Service ───────────────────────────────────────────────────────────────

class AIService:
    """Handles all AI interactions with Gemini or mock fallback."""

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.is_mock = not api_key or api_key == "your_gemini_api_key_here"

        if not self.is_mock:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=SYSTEM_PROMPT,
            )
            print("[OK] AI Service initialized with Gemini API")
        else:
            self.model = None
            print("[MOCK] AI Service running in MOCK mode (no GOOGLE_API_KEY set)")

    def stream_response(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream a response from the AI model given conversation history."""
        if self.is_mock:
            yield from self._mock_stream_response(messages)
            return

        # Build chat history (all except the last message)
        history = []
        for msg in messages[:-1]:
            history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]],
            })

        chat = self.model.start_chat(history=history)
        last_message = messages[-1]["content"]

        response = chat.send_message(last_message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def generate_ticket_summary(self, messages: list[dict]) -> dict:
        """Generate a structured ticket summary from the conversation."""
        if self.is_mock:
            return self._mock_ticket_summary(messages)

        conversation_text = "\n".join(
            f"{'Customer' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in messages
        )

        prompt = TICKET_SUMMARY_PROMPT.format(conversation=conversation_text)
        response = self.model.generate_content(prompt)

        try:
            text = response.text.strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return {
                "title": "Service Required — Unresolved Issue",
                "description": conversation_text[:500],
                "category": "other",
                "priority": "medium",
                "ai_summary": "Automated troubleshooting was unable to resolve the customer's issue.",
            }

    def categorize_issue(self, issue: str) -> str:
        """Categorize an issue description into a predefined category."""
        if self.is_mock:
            return self._mock_categorize(issue)

        prompt = CATEGORY_PROMPT.format(issue=issue)
        response = self.model.generate_content(prompt)
        category = response.text.strip().lower()

        valid = {"battery", "charging", "starting", "app", "infotainment", "tire", "safety", "other"}
        return category if category in valid else "other"

    # ─── Mock Implementations ─────────────────────────────────────────────────

    def _mock_stream_response(self, messages: list[dict]) -> Generator[str, None, None]:
        """Keyword-based mock responses for demo without an API key."""
        last_message = messages[-1]["content"].lower()

        if any(w in last_message for w in ["start", "won't start", "not starting", "dead", "power"]):
            response = self._get_starting_response()
        elif any(w in last_message for w in ["charge", "charging", "plug", "cable", "outlet"]):
            response = self._get_charging_response()
        elif any(w in last_message for w in ["battery", "range", "mile", "percentage", "drain"]):
            response = self._get_battery_response()
        elif any(w in last_message for w in ["app", "phone", "bluetooth", "connect", "pair"]):
            response = self._get_app_response()
        elif any(w in last_message for w in ["screen", "display", "radio", "infotainment", "carplay"]):
            response = self._get_infotainment_response()
        elif any(w in last_message for w in ["tire", "pressure", "flat", "tyre"]):
            response = self._get_tire_response()
        else:
            response = self._get_general_response()

        # Simulate streaming by yielding word chunks
        words = response.split(" ")
        chunk_size = 3
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + chunk_size])
            if i > 0:
                chunk = " " + chunk
            yield chunk
            time.sleep(0.03)

    def _get_starting_response(self) -> str:
        return """I understand how frustrating it is when your vehicle won't start. Let's work through this together.

## Possible Causes
This could be related to the key fob, brake pedal position, or the vehicle's power state.

## Troubleshooting Steps

1. **Check the gear position** — Make sure the vehicle is in **PARK (P)**
2. **Press the brake pedal firmly** — The brake must be fully depressed while pressing the START button
3. **Check your key fob** — Place it directly on the center console's wireless charging pad
4. **Hold the START button** — Press and hold for **5 full seconds** while keeping the brake pressed
5. **Check for dashboard lights** — When you turn the key to ON (without starting), do any warning lights appear?

If none of these steps work, try this reset procedure:
- Open and close the driver's door
- Wait 30 seconds
- Try starting again with the brake firmly pressed

💡 **Pro tip:** If the key fob battery is low, you'll see a small key icon on your dashboard. You can still start the vehicle by placing the fob directly against the START button.

Did any of these steps help resolve the issue?"""

    def _get_charging_response(self) -> str:
        return """I'm sorry you're having charging difficulties. Let's troubleshoot this step by step.

## Possible Causes
Charging issues can stem from the cable connection, the charging port, or the power source.

## Troubleshooting Steps

1. **Check cable connections** — Ensure the charging cable is firmly plugged in at **both ends** (vehicle and outlet/station)
2. **Inspect the charging port light:**
   - 🟢 Green/Blue pulse = Charging normally
   - 🔴 Red/Amber = Error detected
   - ⚫ No light = No connection established
3. **Reset the charging session:**
   - Unplug the cable from the vehicle
   - Wait **30 seconds**
   - Reconnect firmly until you hear a click
4. **Try a different outlet/station** — The power source might be the issue
5. **Check for debris** — Look inside the charging port for any dirt or obstruction

### If Using a Public Charging Station:
- Ensure your account has an active payment method
- Try tapping your card/phone again
- Check if the station shows any error codes

Were any of these steps helpful?"""

    def _get_battery_response(self) -> str:
        return """I understand the concern about your battery range. Let me help you optimize it.

## Understanding Your Range

EV range varies based on several factors. Here's what affects it and how to maximize it:

## Immediate Steps to Extend Range

1. **Enable Eco Mode** — This can extend your range by **15-20%**
   - Go to Settings → Driving → Select "Eco Mode"
2. **Reduce climate control** — A/C and heating are the biggest power consumers
   - Use seat heaters instead of cabin heating (more efficient)
   - Set temperature to a moderate level
3. **Check tire pressure** — Low pressure significantly reduces range
   - Recommended PSI is on the driver's door jamb sticker
   - Each PSI below recommended reduces range by ~0.3%
4. **Smooth driving** — Avoid rapid acceleration and hard braking
   - Use regenerative braking (one-pedal driving if available)
5. **Reduce speed** — Highway speeds above 65 mph significantly reduce range

## Quick Check:
- What is your current battery percentage?
- How far do you need to travel?
- Is the A/C or heater running?

This will help me give you more specific advice."""

    def _get_app_response(self) -> str:
        return """Let's get your app connectivity sorted out. This is usually a quick fix.

## Troubleshooting Steps

1. **Toggle Bluetooth** — Turn Bluetooth off and back on in your phone settings
2. **Toggle Airplane Mode** — Turn it on, wait 10 seconds, then turn it off
3. **Force close the Optimotion app:**
   - iOS: Swipe up from bottom, swipe the app away
   - Android: Recent apps → Swipe the app away
4. **Re-open the app** and try connecting again
5. **Check app permissions:**
   - Location: Must be set to "Always" or "While Using"
   - Bluetooth: Must be enabled
   - Notifications: Enable for alerts

### If Still Not Connecting:
6. **Remove the vehicle from the app** and re-add it:
   - Go to Settings → My Vehicles → Remove Vehicle
   - Re-add using your Vehicle ID
7. **Reinstall the app** — Delete and download fresh from the App Store/Play Store

Are you able to try these steps?"""

    def _get_infotainment_response(self) -> str:
        return """Let's troubleshoot your display/infotainment issue.

## Troubleshooting Steps

1. **Soft reset the display** — Press and hold the power button on the screen for **10 seconds**
2. **Check screen brightness** — It may be turned all the way down
   - Try swiping down on the screen or using the brightness dial
3. **Hard reset** — Hold **both steering wheel scroll wheels** for 10 seconds (if applicable)
4. **Check connections:**
   - For CarPlay: Ensure your iPhone is connected via the correct USB port (not all ports support CarPlay)
   - For Android Auto: Enable USB debugging if prompted
5. **Restart the vehicle** — Turn off, wait 2 minutes, then restart

### If the Screen Is Frozen:
- The system may need a full power cycle
- Turn off the vehicle, open the door, wait 5 minutes
- This forces a complete system shutdown and fresh restart

Did any of these steps resolve the issue?"""

    def _get_tire_response(self) -> str:
        return """Let's address your tire concern right away.

## Troubleshooting Steps

1. **Check the tire pressure warning** — Note which tire(s) are affected on the dashboard display
2. **Find the recommended PSI** — Check the sticker on the driver's door jamb
3. **Visually inspect the tire** — Look for:
   - Obvious punctures or nails
   - Sidewall damage or bulging
   - Significant deflation
4. **If the tire looks intact:**
   - Drive to the nearest gas station or air pump
   - Inflate to the recommended PSI
   - The warning should clear after driving a few miles

### ⚠️ If You Have a Flat Tire:
- **Do NOT drive on it** — This can damage the wheel
- Check the trunk for a tire repair kit or spare
- Use the Optimotion app to request roadside assistance
- Stay in a safe location away from traffic

Is the tire visibly flat, or is this a pressure warning on the dashboard?"""

    def _get_general_response(self) -> str:
        return """Thank you for reaching out. I'd like to help you resolve this issue.

To better assist you, could you provide a bit more detail about what you're experiencing?

Here are some things that would help me diagnose the issue:

1. **What exactly is happening?** — Describe the symptoms you're seeing
2. **When did it start?** — Did it happen suddenly or gradually?
3. **Any warning lights?** — Are there any indicators on the dashboard?
4. **What have you tried?** — Any steps you've already taken?

Common issues I can help with:
- 🚗 Vehicle won't start
- 🔌 Charging problems
- 🔋 Battery/range concerns
- 📱 App connectivity
- 🖥️ Dashboard/infotainment issues
- 🛞 Tire pressure alerts

Please describe your situation and I'll provide specific troubleshooting steps!"""

    def _mock_ticket_summary(self, messages: list[dict]) -> dict:
        """Generate a mock ticket summary based on conversation content."""
        all_text = " ".join(m["content"] for m in messages if m["role"] == "user").lower()

        if any(w in all_text for w in ["start", "power", "dead"]):
            return {
                "title": "Vehicle Won't Start — Troubleshooting Failed",
                "description": "Customer reported the vehicle won't start. Standard troubleshooting steps (key fob, brake pedal, reset procedure) were attempted but did not resolve the issue.",
                "category": "starting",
                "priority": "high",
                "ai_summary": "Multiple starting troubleshooting steps attempted without success. Physical inspection recommended — possible issue with starter motor, 12V battery, or immobilizer system.",
            }
        elif any(w in all_text for w in ["charge", "plug", "cable"]):
            return {
                "title": "Charging Failure — Requires Physical Inspection",
                "description": "Customer unable to charge the vehicle. Cable connections, port inspection, and station reset were attempted.",
                "category": "charging",
                "priority": "high",
                "ai_summary": "Charging troubleshooting unsuccessful. Possible hardware issue with charging port, onboard charger, or cable. Physical inspection needed.",
            }
        else:
            return {
                "title": "Unresolved Vehicle Issue — Service Required",
                "description": "Customer reported an issue that could not be resolved through automated troubleshooting.",
                "category": "other",
                "priority": "medium",
                "ai_summary": "The customer's issue persisted after multiple troubleshooting attempts. A physical inspection by a service technician is recommended.",
            }

    def _mock_categorize(self, issue: str) -> str:
        """Keyword-based categorization fallback."""
        issue_lower = issue.lower()
        categories = {
            "starting": ["start", "power", "ignition", "dead", "won't turn"],
            "charging": ["charge", "plug", "cable", "outlet", "station"],
            "battery": ["battery", "range", "mile", "drain", "percentage"],
            "app": ["app", "phone", "bluetooth", "connect", "pair"],
            "infotainment": ["screen", "display", "radio", "carplay", "android auto"],
            "tire": ["tire", "tyre", "pressure", "flat", "psi"],
            "safety": ["smoke", "fire", "accident", "brake", "airbag", "warning"],
        }
        for cat, keywords in categories.items():
            if any(kw in issue_lower for kw in keywords):
                return cat
        return "other"


# ─── Singleton ────────────────────────────────────────────────────────────────

ai_service = AIService()
