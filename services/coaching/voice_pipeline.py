
import time
import logging
import streamlit as st

# Setup logging
logger = logging.getLogger(__name__)


class VoicePipeline:

    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0

    # Find exercise form mistakes
    def _find_form_issue(self, exercise, metrics):

        if not metrics:
            return None

        if "issue" in metrics:
            return metrics["issue"]

        # Squats
        if exercise == "Squats":
            knee_angle = metrics.get("knee_angle")

            if knee_angle is not None and knee_angle > 120:
                return "Bend your knees more while squatting."

        # Push-ups
        elif exercise == "Push-ups":
            body_angle = metrics.get("body_angle")

            if body_angle is not None and body_angle < 160:
                return "Keep your body straight during push-ups."

        # Biceps Curls
        elif exercise == "Biceps Curls":
            elbow_angle = metrics.get("elbow_angle")

            if elbow_angle is not None and elbow_angle > 160:
                return "Focus on controlling your biceps curl."

        # Shoulder Press
        elif exercise == "Shoulder Press":
            elbow_angle = metrics.get("elbow_angle")

            if elbow_angle is not None and elbow_angle < 60:
                return "Check your shoulder press arm position."

        # Lunges
        elif exercise == "Lunges":
            knee_angle = metrics.get("knee_angle")

            if knee_angle is not None and knee_angle > 120:
                return "Bend your front knee more during lunges."

        return None

    # Process workout events and generate coaching
    def process_event(self, event, exercise, metrics):

        try:
            issue = self._find_form_issue(exercise, metrics or {})

            now = time.time()

            # Important workout events
            is_major_issue = event in [
                "workout_started",
                "set_completed",
                "workout_completed"
            ]

            # Avoid repeated live feedback
            if not is_major_issue:

                if not issue:
                    return None

                # Speak only once every 5 seconds
                if now - self.last_spoken_at < 5:
                    return None

            # Generate feedback using Groq
            text = self.llm.give_feedback(event, issue)

            if not text:
                return None

            # Convert feedback text into speech
            voice = self.tts.speak(text)

            # Save last spoken time
            self.last_spoken_at = now

            return voice, text

        except Exception:
            logger.exception("Voice coaching failed")
            return None


# Play generated audio in Streamlit
def autoplay_audio(audio_bytes):

    if not audio_bytes:
        return

    try:
        st.audio(
            audio_bytes,
            format="audio/mp3",
            autoplay=True
        )

    except Exception:
        logger.exception("Audio playback failed")
