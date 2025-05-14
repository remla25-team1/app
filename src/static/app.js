async function analyze() {
    const tweet = document.getElementById("tweet").value;
    const resultDiv = document.getElementById("result");
    resultDiv.textContent = "Analyzing...";
    try {
      const response = await fetch("/sentiment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tweet })
      });
  
      if (!response.ok) {
        throw new Error("Request failed");
      }
  
      const data = await response.json();
      if (data.result == "positive"){
        resultDiv.textContent = "😇 Positive";
      }else if (data.result == "negative"){
        resultDiv.textContent = "😈 Negative";
      }else{
        resultDiv.textContent = "😶‍🌫️ Neutral";
      }
      window._latestFeedback = {
        tweet: tweet,
        prediction: data.result
      };
      showFeedback();
    } catch (err) {
      resultDiv.textContent = "Error: " + err.message;
    }
  }
  

  async function getVersion() {
    const versionDiv = document.getElementById("version");
    try {
      const res = await fetch("/version");
      if (!res.ok) throw new Error("Failed to fetch version");
      const data = await res.json();
      versionDiv.textContent = `Lib Version: ${data.lib_version}, \n App Version: ${data.app_version}, \n model Version ${data.model_version}`;
    } catch (err) {
      versionDiv.textContent = "Version: unknown";
    }
  }
  
  window.onload = () => {
    getVersion();
  };
  
  
  function showCorrection() {
    document.getElementById("correction-area").classList.remove("hidden");
    document.getElementById("feedback-msg").textContent = "";
  }
  
  function hideCorrection() {
    document.getElementById("correction-area").classList.add("hidden");
  }
  
  function sendFeedback(isCorrect) {
    const correctionMsg = document.getElementById("correction-msg");
    if (!isCorrect) {
      hideFeedback();
      showCorrection();
    }else{
      hideFeedbackButtons();
      correctionMsg.textContent = "Thank you for your feedback!"
    }
  }

  function showFeedback() {
    document.getElementById("feedback").classList.remove("hidden");
  }

  function hideFeedback() {
    document.getElementById("feedback").classList.add("hidden");
  }

  function hideCorrectionButtons() {
    document.getElementById("correction-buttons").classList.add("hidden");
  }
  
  function hideFeedbackButtons(){
    document.getElementById("feedback-buttons").classList.add("hidden");
  }
  
    async function submitCorrection(correctLabel) {
    const correctionMsg = document.getElementById("correction-msg");
    const { tweet, prediction } = window._latestFeedback || {};
    if (!tweet || !prediction) {
      correctionMsg.textContent = "No context to correct.";
      return;
    }
    try {
      const response = await fetch("/correction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tweet:tweet,
          prediction: prediction,
          correction: correctLabel
        })
      });
      if (!response.ok){
        correctionMsg.textContent = "Oops, Failed to submit correction:(, try again.";
      }else{
      hideCorrectionButtons();
      correctionMsg.textContent = "Thank you for your correction!";
      }
    } catch (err) {
      correctionMsg.textContent = "Error: " + err.message;
    }
  }
  