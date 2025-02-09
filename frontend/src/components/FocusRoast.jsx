import "../styling/FocusRoast.css";
import axios from "axios";
import { useState, useRef, useCallback, useEffect } from "react";
import { Link } from "react-router-dom";
import focusRoastImage from "../assets/focus_roast_main.svg";
import MatchaModeImage from "../assets/matcha_mode_white.svg";

function FocusRoast() {
  const [isStudying, setIsStudying] = useState(false);
  const [audioSrc, setAudioSrc] = useState(null);
  const [coach, setCoach] = useState("David Goggins");

  const isCapturingRef = useRef(false);
  const screenStreamRef = useRef(null);
  const webcamStreamRef = useRef(null);

  useEffect(() => {
    if (coach === "Gordon Ramsay") {
      const gordonRamsay = document.querySelector(".GordonRamsay");
      gordonRamsay.style.border = "2px solid black";
      const davidGoggin = document.querySelector(".DavidGoggins");
      davidGoggin.style.border = "0px solid black";
    } else {
      const davidGoggin = document.querySelector(".DavidGoggins");
      davidGoggin.style.border = "2px solid black";
      const gordonRamsay = document.querySelector(".GordonRamsay");
      gordonRamsay.style.border = "0px solid black";
    }
    console.log(coach);
  }, [coach]);

  // --- Coach Selection Handlers ---
  const addBlackBorder = () => {
    setCoach("Gordon Ramsay");
  };
  const addBlackBorder2 = () => {
    setCoach("David Goggins");
  };

  // --- Start capturing both screen & webcam ---
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

      // Request webcam
      webcamStreamRef.current = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      // Begin the loop
      captureAndSendImages();
    } catch (error) {
      console.error("Error accessing screen/webcam:", error);
      setIsStudying(false);
      isCapturingRef.current = false;
    }
  };

  // --- Stop capturing session ---
  const stopStudying = () => {
    setIsStudying(false);
    isCapturingRef.current = false;

    // Stop screen stream
    if (screenStreamRef.current) {
      screenStreamRef.current.getTracks().forEach((track) => track.stop());
      screenStreamRef.current = null;
    }
    // Stop webcam stream
    if (webcamStreamRef.current) {
      webcamStreamRef.current.getTracks().forEach((track) => track.stop());
      webcamStreamRef.current = null;
    }
  };

  // --- Helper: Capture one frame from a given stream as Base64 ---
  const captureFrame = async (stream) => {
    const video = document.createElement("video");
    video.srcObject = stream;
    await video.play(); // Wait for the video to be ready

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL("image/png"); // "data:image/png;base64,iVBOR..."
  };

  // --- Main loop: Capture both images, send them, receive MP3 ---
  const captureAndSendImages = useCallback(async () => {
    if (!isCapturingRef.current) return;

    try {
      // 1) Capture screen
      const screenData = await captureFrame(screenStreamRef.current);

      // 2) Capture webcam
      const webcamData = await captureFrame(webcamStreamRef.current);

      // 3) Send both images + coach to Flask
      const response = await axios.post(
        "/api/process-image",
        {
          screenImage: screenData,
          webcamImage: webcamData,
          coach: coach,
        },
        { responseType: "blob" } // Expect MP3 as binary
      );
      console.log("Sent coach:", coach);

      // 4) Check for MP3
      const audioBlob = response.data;
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
      console.error("Error capturing or sending images:", error);
    } finally {
      // 5) Wait 5s & repeat
      setTimeout(() => {
        if (isCapturingRef.current) captureAndSendImages();
      }, 3000);
    }
  }, [coach]);

  // --- Toggle start/stop on the same button ---
  const handleStartStudy = () => {
    const startButton = document.querySelector(".startButton");
    if (isStudying) {
      // Was studying → Stop
      startButton.textContent = "Start Studying";
      stopStudying();
    } else {
      // Was not studying → Start
      startButton.textContent = "Stop Studying";
      startStudying();
    }
  };

  return (
    <div className="FocusRoastMain">
      <img src={focusRoastImage} className="FocusRoastImage" alt="focus_roast" />
      <Link to="/" className="MatchaModeLink">
        <img src={MatchaModeImage} className="MatchaModeImage" alt="matcha_mode" />
      </Link>
      <div className="coachSelect">
        <h2 id="chooseYourCoach">Choose your coach</h2>
        <button className="GordonRamsay" onClick={addBlackBorder}>
          Gordon Ramsay
        </button>
        <button className="DavidGoggins" onClick={addBlackBorder2}>
          David Goggins
        </button>
      </div>
      <div className="startStopButtons">
        <button className="startButton" onClick={handleStartStudy}>
          Start Studying
        </button>
      </div>

      {/* Audio playback element, if any */}
      {audioSrc && (
        <audio controls autoPlay src={audioSrc} style={{ display: 'none' }}>
          Your browser does not support the audio element.
        </audio>
      )}
    </div>
  );
}

export default FocusRoast;
