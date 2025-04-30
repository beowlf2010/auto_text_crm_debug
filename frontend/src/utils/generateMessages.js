// src/utils/generateMessages.js

const API_KEY = "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"; // ← Your real API key

const generateMessages = async (leads) => {
  const prompts = leads.map((lead) => {
    const name = lead.FirstName || lead.Name || "there";
    const vehicle = lead.Vehicle || lead.Interest || lead.Model || "a new vehicle";
    return `Write a friendly, professional text message for a car salesperson to follow up with a lead named ${name} who showed interest in ${vehicle}. Keep it short and engaging.`;
  });

  const responses = await Promise.all(
    prompts.map(async (prompt) => {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${API_KEY}`,
        },
        body: JSON.stringify({
          model: "gpt-3.5-turbo",
          messages: [{ role: "user", content: prompt }],
          temperature: 0.7,
        }),
      });

      const json = await response.json();
      return json?.choices?.[0]?.message?.content || "No message generated";
    })
  );

  return responses;
};

export default generateMessages;
