document.addEventListener("DOMContentLoaded", async () => {
  const results = document.getElementById("results");

  try {
    const res = await fetch("/api/trends");
    const data = await res.json();

    if (data.error) {
      results.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
      return;
    }

    results.innerHTML = "";
    data.forEach(item => {
      const div = document.createElement("div");
      div.className = "topic";
      div.innerHTML = `
        <div class="orig"><b>${item.original}</b></div>
        <div class="par">${item.paraphrased}</div>
      `;
      results.appendChild(div);
    });
  } catch (err) {
    results.innerHTML = `<p style="color:red;">Fetch failed: ${err}</p>`;
  }
});
