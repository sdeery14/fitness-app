// Voice Activity Detection (VAD) for Fitness App
// Based on: https://github.com/bklieger-groq/gradio-groq-basics/tree/main/calorie-tracker

async function main() {
  const script1 = document.createElement("script");
  script1.src = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/ort.js";
  document.head.appendChild(script1);
  
  const script2 = document.createElement("script");
  script2.onload = async () => {
    console.log("🎤 VAD loaded");
    
    // Update record button text
    var record = document.querySelector('.record-button');
    if (record) {
      record.textContent = "Just Start Talking!";
    }
    
    const myvad = await vad.MicVAD.new({
      onSpeechStart: () => {
        console.log("🎤 Speech detected - starting recording");
        var record = document.querySelector('.record-button');
        var player = document.querySelector('#streaming-out');
        if (record != null && (player == null || player.paused)) {
          record.click();
        }
      },
      onSpeechEnd: (audio) => {
        console.log("� Speech ended - stopping recording");
        var stop = document.querySelector('.stop-button');
        if (stop != null) {
          stop.click();
        }
      }
    });
    
    // Monitor voice conversation status and control VAD
    let vadStarted = false;
    
    function checkVoiceStatus() {
      const statusElement = document.querySelector('#voice-status');
      const isVoiceActive = statusElement && statusElement.style.display !== 'none';
      
      if (isVoiceActive && !vadStarted) {
        console.log("� Starting VAD monitoring");
        myvad.start();
        vadStarted = true;
      } else if (!isVoiceActive && vadStarted) {
        console.log("⏸️ Stopping VAD monitoring");
        myvad.pause();
        vadStarted = false;
      }
    }
    
    // Check status every second
    setInterval(checkVoiceStatus, 1000);
    console.log("✅ VAD initialized successfully");
  };
  
  script2.src = "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.7/dist/bundle.min.js";
  document.head.appendChild(script2);
}

// Initialize when document is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', main);
} else {
  main();
}
