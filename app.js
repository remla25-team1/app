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
      resultDiv.textContent = `Prediction: ${data.result}`;
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
      versionDiv.textContent = `Version: ${data.version}`;
    } catch (err) {
      versionDiv.textContent = "Version: unknown";
    }
  }
  