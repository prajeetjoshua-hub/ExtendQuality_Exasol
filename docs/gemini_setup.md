# Gemini VLM setup

EXtendQuality sends an image to Gemini only when the local decision engine marks
the case uncertain. Confident YOLO decisions remain local. The human inspector
always makes the final decision.

## Configure the secret

1. Create a Gemini API key in Google AI Studio.
2. In the repository root, create a file named `.env.local`.
3. Add these lines and replace the placeholder with the real key:

   ```text
   EXTENDQUALITY_VLM_PROVIDER=gemini
   EXTENDQUALITY_VLM_API_KEY=PASTE_THE_KEY_HERE
   EXTENDQUALITY_VLM_MODEL=gemini-3.6-flash
   EXTENDQUALITY_VLM_TIMEOUT_SECONDS=45
   ```

4. Stop and restart the demo. The launcher reads `.env.local` into the backend
   process and never prints its values.
5. Confirm that the dashboard header says `GEMINI READY`.

`.env.local` is ignored by Git. Never paste the key into React, screenshots,
documentation, a commit, or a chat message.

## Prove the routing

1. Run a confident prepared image. The VLM mode should be `NOT REQUIRED`.
2. Run the prepared uncertain image. With Internet access, the mode should be
   `GEMINI` and its wording should be specific to the captured evidence.
3. Disconnect the Internet and repeat the uncertain case. The inspection must
   still complete with `OFFLINE FALLBACK`.

The configured `gemini-3.6-flash` model accepts image input and structured output.
The adapter requests two JSON fields: `observation` and `recommended_action`.
