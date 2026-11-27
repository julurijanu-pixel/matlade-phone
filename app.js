const smsInput = document.getElementById("smsInput");
const convertBtn = document.getElementById("convertBtn");
const speakBtn = document.getElementById("speakBtn");
const stopBtn = document.getElementById("stopBtn");
const teluguOutput = document.getElementById("teluguOutput");
const extractedInfo = document.getElementById("extractedInfo");
const voiceStatus = document.getElementById("voiceStatus");
const historyList = document.getElementById("historyList");
const sampleButtons = document.querySelectorAll(".sample-btn");

let latestTeluguText = "";

sampleButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    smsInput.value = btn.getAttribute("data-sms") || "";
    runConversion(true);
  });
});

async function runConversion(autoSpeak = false) {
  const smsText = smsInput.value.trim();
  if (!smsText) {
    teluguOutput.textContent = "Please enter an English SMS first.";
    return;
  }

  convertBtn.disabled = true;
  convertBtn.textContent = "Converting...";

  try {
    const response = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sms_text: smsText }),
    });
    const data = await response.json();

    if (!response.ok || !data.ok) {
      teluguOutput.textContent = data.error || "Could not convert SMS.";
      return;
    }

    latestTeluguText = data.telugu_text;
    teluguOutput.textContent = data.telugu_text;

    const ext = data.extracted || {};
    extractedInfo.textContent =
      `Type: ${data.category.toUpperCase()} | Amount: ${ext.amount || "-"} | Balance: ${ext.balance || "-"} | Date: ${ext.date || "-"}`;

    renderHistory(data.history || []);

    if (autoSpeak) {
      speakTelugu(latestTeluguText);
    }
  } catch (err) {
    teluguOutput.textContent = "Network error while contacting local server.";
  } finally {
    convertBtn.disabled = false;
    convertBtn.textContent = "Convert to Telugu";
  }
}

function speakTelugu(textToSpeak) {
  const target = (textToSpeak || latestTeluguText || teluguOutput.textContent || "").trim();
  if (!target) return;

  if (!("speechSynthesis" in window)) {
    voiceStatus.textContent = "Browser speech synthesis not supported — read the Telugu text shown above.";
    return;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(target);
  utterance.lang = "te-IN";
  utterance.rate = 0.95;

  const voices = window.speechSynthesis.getVoices();
  const teluguVoice = voices.find((v) => v.lang && v.lang.toLowerCase().startsWith("te"));
  if (teluguVoice) {
    utterance.voice = teluguVoice;
    voiceStatus.textContent = `Speaking in Telugu (${teluguVoice.name})...`;
  } else {
    voiceStatus.textContent = "Speaking with te-IN fallback (if silent on your device, install Telugu TTS voice in OS settings).";
  }

  utterance.onend = () => {
    voiceStatus.textContent = "Finished reading Telugu message.";
  };
  utterance.onerror = () => {
    voiceStatus.textContent = "Audio playback unavailable on this browser — Telugu text is displayed above.";
  };

  window.speechSynthesis.speak(utterance);
}

function renderHistory(items) {
  if (!items.length) {
    historyList.textContent = "No readouts in this session yet.";
    return;
  }
  historyList.innerHTML = items
    .map(
      (item) =>
        `<div class="history-item"><strong>[${item.timestamp}] ${item.category.toUpperCase()}:</strong> ${item.telugu_text}</div>`
    )
    .join("");
}

convertBtn.addEventListener("click", () => runConversion(false));
speakBtn.addEventListener("click", () => speakTelugu(latestTeluguText));
stopBtn.addEventListener("click", () => {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    voiceStatus.textContent = "Voice stopped.";
  }
});

window.addEventListener("DOMContentLoaded", () => {
  runConversion(false);
});