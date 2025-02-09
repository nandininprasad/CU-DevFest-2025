import { useState, useRef, useCallback } from "react";
import "../styling/StudyKitchen.css";
import html2canvas from "html2canvas";
import axios from "axios";

function StudyKitchen() {

    const [isStudying, setIsStudying] = useState(false);
    const [audioSrc, setAudioSrc] = useState(null);
    
    const isCapturingRef = useRef(false);
    const screenStreamRef = useRef(null);
    

  // Start capturing session once (ask for permission just once)
  const startStudying = async () => {
    if (isStudying) return; // Avoid duplicates
    setIsStudying(true);
    isCapturingRef.current = true;

    try {
      // Request screen sharing once
      screenStreamRef.current = await navigator.mediaDevices.getDisplayMedia({
        video: { mediaSource: "screen" },
        audio: false,
      });
      // Begin the loop
      captureAndSendScreen();
    } catch (error) {
      console.error("Error accessing screen:", error);
      setIsStudying(false);
      isCapturingRef.current = false;
    }
  };

  // Stop capturing session
  const stopStudying = () => {
    setIsStudying(false);
    isCapturingRef.current = false;
    // Stop the screen stream
    if (screenStreamRef.current) {
      screenStreamRef.current.getTracks().forEach((track) => track.stop());
      screenStreamRef.current = null;
    }
  };

  // Capture loop
  const captureAndSendScreen = useCallback(async () => {
    if (!isCapturingRef.current || !screenStreamRef.current) return;

    try {
      // 1. Create video with existing stream
      const video = document.createElement("video");
      video.srcObject = screenStreamRef.current;
      await video.play();

      // 2. Draw one frame to an off-screen canvas
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // 3. Convert canvas to base64
      const imageData = canvas.toDataURL("image/png");

      // 4. Send screenshot to Flask. 
      //    IMPORTANT: set { responseType: "blob" } so we receive MP3 binary.
      const response = await axios.post(
        "/api/process-image",
        { image: imageData },
        { responseType: "blob" }
      );

      // 5. We got an MP3 in the same call. Let's play it:
      const audioBlob = response.data; // The MP3 file
      console.log("size is", audioBlob.size)
      if (audioBlob && audioBlob.size > 0) {
        console.log("Received MP3 file. Size:", audioBlob.size);
        const blobUrl = URL.createObjectURL(audioBlob);
        setAudioSrc(blobUrl);

        const audioElement = new Audio(blobUrl);
        await audioElement.play().catch((err) => {
          console.error("Audio auto-play failed:", err);
        });
      } else {
        console.log("No audio or empty audio received.");
      }
    } catch (error) {
      console.error("Error capturing or sending screenshot:", error);
    } finally {
      // Wait 5s and repeat
      setTimeout(() => {
        if (isCapturingRef.current) captureAndSendScreen();
      }, 20_000);
    }
  }, []);

    const fetchAudio = async (text) => {
        try {
            const response = await axios.post(
                "/api/generate-audio",
                {data},
                { responseType: "blob"}
            );

            const blob = new Blob([response.data], {type: "audio/mpeg"});
            const audioUrl = URL.createObjectURL(blob)
            setAudioSrc(audioUrl);
            console.log(audioUrl)
            // Auto-play for testing
            const audioElement = new Audio(audioUrl);
            audioElement.play().catch((error) => {
            console.error("Auto-play failed:", error);
    });
        } catch (error) {
            console.error("Error generating audio:", error);
          }

    }

    return (
        <div style={{ padding: "2rem" }}>
        <h1>Study Kitchen</h1>
        <button onClick={startStudying} disabled={isStudying}>
          Start Studying
        </button>
        <button onClick={stopStudying} disabled={!isStudying}>
          Stop Studying
        </button>
  
        {audioSrc && (
          <div style={{ marginTop: "1rem" }}>
            <audio controls autoPlay src={audioSrc}>
              Your browser does not support the audio element.
            </audio>
          </div>
        )}
      </div>
  
    )
}

export default StudyKitchen;
