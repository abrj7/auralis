/**
 * AudioController Component
 * Handles audio recording (input) and audio playback (output)
 * Uses ElevenLabs STT/TTS via backend API
 */
"use client";

import { useState, useEffect, useRef } from "react";
import { AudioRecorder, playAudio } from "@/lib/audioUtils";

interface AudioControllerProps {
  onTranscript?: (text: string) => void;
  onSpeakingStateChange?: (isSpeaking: boolean) => void;
}

export default function AudioController({
  onTranscript,
  onSpeakingStateChange,
}: AudioControllerProps) {
  const [isListening, setIsListening] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [hasPermission, setHasPermission] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);

  const recorderRef = useRef<AudioRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Initialize audio recorder
    recorderRef.current = new AudioRecorder();

    // Check microphone permission
    checkMicrophonePermission();

    return () => {
      // Cleanup
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const checkMicrophonePermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
      setHasPermission(true);
    } catch (err) {
      setHasPermission(false);
      setError("Microphone permission denied");
    }
  };

  const handleRecordingComplete = async (audioBlob: Blob) => {
    try {
      setError(null);
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      const response = await fetch("http://localhost:8000/api/stt", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("STT request failed");
      }

      const data = await response.json();
      if (data.text) {
        setTranscript(data.text);
        onTranscript?.(data.text);

        // Mock chat response (replace with real API when Person 3 is ready)
        await handleChatResponse(data.text);
      }
    } catch (err) {
      console.error("Transcription error:", err);
      setError("Failed to transcribe audio");
    }
  };

  const handleChatResponse = async (userMessage: string) => {
    try {
      // Mock response - replace with real /api/chat when Person 3 is ready
      const mockResponse = {
        response: "I understand. Can you tell me more about your symptoms?",
        followup_needed: true,
      };

      // Send to TTS
      await speakText(mockResponse.response);
    } catch (err) {
      console.error("Chat error:", err);
      setError("Failed to get response");
    }
  };

  const speakText = async (text: string) => {
    try {
      setError(null);
      const response = await fetch("http://localhost:8000/api/tts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error("TTS request failed");
      }

      const data = await response.json();

      if (data.audio_base64) {
        // Convert base64 to playable URL
        const audioUrl = `data:audio/mpeg;base64,${data.audio_base64}`;

        // Emit event for avatar
        window.dispatchEvent(new CustomEvent("audioPlaybackStart"));

        await playAudio(
          audioUrl,
          () => {
            setIsPlaying(true);
            onSpeakingStateChange?.(true);
          },
          () => {
            setIsPlaying(false);
            onSpeakingStateChange?.(false);
            window.dispatchEvent(new CustomEvent("audioPlaybackEnd"));
          },
          (error) => {
            setError(error);
            setIsPlaying(false);
            onSpeakingStateChange?.(false);
          }
        );
      }
    } catch (err) {
      console.error("TTS error:", err);
      setError("Failed to generate speech");
    }
  };

  const startListening = async () => {
    if (!hasPermission) {
      await checkMicrophonePermission();
      return;
    }

    try {
      setError(null);
      if (recorderRef.current) {
        await recorderRef.current.startRecording();
        setIsListening(true);
      }
    } catch (err) {
      console.error("Recording start error:", err);
      setError("Failed to start recording");
    }
  };

  const stopListening = async () => {
    try {
      if (recorderRef.current && recorderRef.current.isRecording()) {
        const audioBlob = await recorderRef.current.stopRecording();
        await handleRecordingComplete(audioBlob);
        setIsListening(false);
      }
    } catch (err) {
      console.error("Recording stop error:", err);
      setError("Failed to stop recording");
      setIsListening(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4 p-6">
      {/* Microphone button */}
      <button
        onClick={isListening ? stopListening : startListening}
        disabled={isPlaying || !hasPermission}
        className={`p-6 rounded-full transition-all shadow-lg ${
          isListening
            ? "bg-red-500 hover:bg-red-600 animate-pulse"
            : isPlaying
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-blue-600 hover:bg-blue-700"
        }`}
        aria-label={isListening ? "Stop listening" : "Start listening"}
      >
        <svg
          className="w-8 h-8 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
          />
        </svg>
      </button>

      {/* Status text */}
      <div className="text-center min-h-[24px]">
        {!hasPermission && (
          <p className="text-sm text-red-600">Microphone permission needed</p>
        )}
        {hasPermission && isListening && (
          <p className="text-sm text-red-600 font-medium">🎤 Listening...</p>
        )}
        {hasPermission && isPlaying && (
          <p className="text-sm text-blue-600 font-medium">
            🔊 Doctor is speaking...
          </p>
        )}
        {hasPermission && !isListening && !isPlaying && (
          <p className="text-sm text-gray-500">Click to speak</p>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="max-w-md p-3 bg-red-100 border border-red-300 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Live transcript */}
      {transcript && (
        <div className="max-w-md p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">You said:</p>
          <p className="text-sm text-gray-800">{transcript}</p>
        </div>
      )}

      {/* Mute toggle (for future use) */}
      <button
        onClick={() => setIsMuted(!isMuted)}
        className="text-sm text-gray-600 hover:text-gray-800"
      >
        {isMuted ? "🔇 Unmute" : "🔊 Mute"}
      </button>
    </div>
  );
}
