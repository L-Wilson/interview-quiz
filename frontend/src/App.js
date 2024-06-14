import axios from "axios";
import React, { useState } from "react";

function InterviewQuizButton() {
  const [question, setQuestion] = useState("");

  const handleButtonClick = async () => {
    try {
      const response = await axios.post("/get-question");
      setQuestion(response.data.question);
    } catch (error) {
      console.error("Error fetching question:", error);
    }
  };

  return (
    <div>
      <button onClick={handleButtonClick}>Quiz me</button>
      {question && <p>{question}</p>}
    </div>
  );
}

export default InterviewQuizButton;
