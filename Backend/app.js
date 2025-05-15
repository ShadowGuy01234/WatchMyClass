import { OpenAI } from "openai";
import dotenv from "dotenv";
import express from "express"; // Add this line

const baseURL = "https://api.aimlapi.com/v1";

dotenv.config();

const apiKey = process.env.API_KEY;

const api = new OpenAI({
  apiKey,
  baseURL,
});

const app = express();
app.use(express.json());

// Image analysis endpoint
app.post("/analyze-image", async (req, res) => {
  const { imageUrl } = req.body;
  if (!imageUrl) {
    return res.status(400).json({ error: "imageUrl is required" });
  }

  try {
    const completion = await api.chat.completions.create({
      model: "openai/gpt-4.1-nano-2025-04-14",
      messages: [
        {
          role: "system",
          content: "You are an expert AI classroom observer specialized in educational psychology and student engagement analysis. Your task is to analyze classroom images and provide detailed, structured feedback in precise JSON format. Be objective, accurate, and focus on actionable insights. Always return valid JSON with no additional text or explanations outside the JSON structure."
        },
        {
          role: "user",
          content: [
            {
              type: "text",
              text: `
You are an intelligent classroom assistant.

I am giving you the URL of a classroom image. Your task is to analyze the image and return a single JSON response containing the following:

Carefully detect and number all visible students from left to right based on their seating position. Include all students, even if partially visible.

For each student, analyze:
- Facial expression
- Emotional state
- Engagement level (1 to 10)
- Whether they need additional attention
- A short observation (notes)

Also, include a classroom summary with:
- totalStudents: Total number of students detected
- averageEngagement: Average engagement score
- dominantMood: One of ["engaged", "distracted", "confused", "tired", "motivated"]
- engagementPercentage: Percentage of students with engagementLevel > 6
- attentiveCount: Number of students with engagementLevel > 6
- distractedCount: Number of students with engagementLevel ≤ 6

Additionally, include a teacherFeedbackReport object that summarizes and gives suggestions based on the data. It should have:

- overallSummary: General emotional tone and engagement of the class
- attentionNeeded: IDs of students needing support with a short reason for each
- teachingStrategies: 2–3 strategies to improve engagement and participation
- followUpRecommendations: Actions for students showing sadness, confusion, or fatigue
- teachingEffectiveness: Short evaluation of the teacher’s performance based on class dynamics

The final output should be a single JSON object with the following structure:

{
  "students": [...],
  "classroomSummary": { ... },
  "teacherFeedbackReport": {
    "overallSummary": "...",
    "attentionNeeded": [ { "id": ..., "reason": "..." }, ... ],
    "teachingStrategies": [ "...", "..." ],
    "followUpRecommendations": [ "...", "..." ],
    "teachingEffectiveness": "..."
  }
}
              `,
            },
            { type: "image_url", image_url: { url: imageUrl } },
          ],
        },
      ],
      max_tokens: 5000,
    });

    const response = completion.choices[0].message.content;
    res.json({ result: response });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
