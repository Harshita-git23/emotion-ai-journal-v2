
import { useEffect, useRef, useState } from "react";
import {
  Mic,
  Square,
  Pause,
  Play,
  RotateCcw,
  AlertCircle,
  AudioLines,
  CheckCircle,
  LoaderCircle,
} from "lucide-react";
import api from "../services/api";

export default function VoiceJournal() {
  const [status, setStatus] = useState("idle");
  const [title, setTitle] = useState("");
  const [audioUrl, setAudioUrl] = useState(null);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [error, setError] = useState("");
  const [recordedBlob, setRecordedBlob] = useState(null);

  const [saving, setSaving] = useState(false);
  const [experienceId, setExperienceId] = useState(null);
  const [saveError, setSaveError] = useState("");

  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);

  const recorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const intervalRef = useRef(null);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    return `${String(minutes).padStart(2, "0")}:${String(
      remainingSeconds
    ).padStart(2, "0")}`;
  };

  const startTimer = () => {
    clearInterval(intervalRef.current);

    intervalRef.current = setInterval(() => {
      setRecordingSeconds((previous) => previous + 1);
    }, 1000);
  };

  const stopTimer = () => {
    clearInterval(intervalRef.current);
    intervalRef.current = null;
  };

  const startRecording = async () => {
    try {
      setError("");

      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error(
          "Audio recording is unavailable. Use a supported browser and a secure connection."
        );
      }

      if (!window.MediaRecorder) {
        throw new Error("Your browser does not support audio recording.");
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      streamRef.current = stream;

      const mimeTypes = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/mp4",
      ];

      const supportedType = mimeTypes.find((type) =>
        MediaRecorder.isTypeSupported(type)
      );

      const recorder = supportedType
        ? new MediaRecorder(stream, { mimeType: supportedType })
        : new MediaRecorder(stream);

      recorderRef.current = recorder;
      chunksRef.current = [];

      setRecordedBlob(null);
      setExperienceId(null);
      setAnalysisResult(null);
      setAnalysisError("");
      setSaveError("");

      setAudioUrl((previous) => {
        if (previous) URL.revokeObjectURL(previous);
        return null;
      });

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });

        setRecordedBlob(blob);

        if (blob.size > 0) {
          const url = URL.createObjectURL(blob);

          setAudioUrl((previous) => {
            if (previous) URL.revokeObjectURL(previous);
            return url;
          });
        } else {
          setError("No audio was captured. Please try again.");
        }

        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      };

      recorder.start();
      setRecordingSeconds(0);
      setStatus("recording");
      startTimer();
    } catch (err) {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;

      setStatus("idle");
      setError(
        err.name === "NotAllowedError"
          ? "Microphone permission was denied. Please allow microphone access."
          : err.message || "Could not start recording."
      );
    }
  };

  const pauseRecording = () => {
    if (recorderRef.current?.state === "recording") {
      recorderRef.current.pause();
      stopTimer();
      setStatus("paused");
    }
  };

  const resumeRecording = () => {
    if (recorderRef.current?.state === "paused") {
      recorderRef.current.resume();
      startTimer();
      setStatus("recording");
    }
  };

  const stopRecording = () => {
    if (
      recorderRef.current &&
      recorderRef.current.state !== "inactive"
    ) {
      recorderRef.current.stop();
    }

    stopTimer();
    setStatus("ready");
  };

  const discardRecording = () => {
    if (recorderRef.current?.state !== "inactive") {
      recorderRef.current?.stop();
    }

    setRecordedBlob(null);
    setExperienceId(null);
    setAnalysisResult(null);
    setAnalysisError("");
    setSaveError("");

    stopTimer();

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;

    setAudioUrl((previous) => {
      if (previous) URL.revokeObjectURL(previous);
      return null;
    });

    chunksRef.current = [];
    recorderRef.current = null;
    setRecordingSeconds(0);
    setStatus("idle");
    setError("");
  };

  const handleAnalyzeSpeech = async (savedExperienceId) => {
    if (!savedExperienceId || !recordedBlob || analyzing) return;

    setAnalyzing(true);
    setAnalysisError("");
    setAnalysisResult(null);

    try {
      const formData = new FormData();

      const extension = recordedBlob.type.includes("mp4")
        ? "mp4"
        : recordedBlob.type.includes("ogg")
        ? "ogg"
        : recordedBlob.type.includes("wav")
        ? "wav"
        : "webm";

      formData.append(
        "audio",
        recordedBlob,
        `voice-recording.${extension}`
      );

      const response = await api.post(
        `/experiences/${savedExperienceId}/analyze/speech`,
        formData
      );

      setAnalysisResult(response.data);
    } catch (err) {
      setAnalysisError(
        err.response?.data?.detail ||
          "Speech analysis failed. Your entry is still saved. You can retry."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSaveEntry = async () => {
    if (experienceId || saving || !recordedBlob) return;

    setSaving(true);
    setSaveError("");

    try {
      const response = await api.post("/experiences/", {
        title: title.trim() || null,
        input_mode: "voice",
        emotions: [],
      });

      const savedId = response.data.id;

      setExperienceId(savedId);

      // Start speech analysis only after the entry has been saved.
      await handleAnalyzeSpeech(savedId);
    } catch (err) {
      setSaveError(
        err.response?.data?.detail || "Failed to save voice entry."
      );
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    return () => {
      stopTimer();

      if (
        recorderRef.current &&
        recorderRef.current.state !== "inactive"
      ) {
        recorderRef.current.stop();
      }

      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <p className="text-xs font-bold uppercase tracking-widest text-[#858fe8]">
          YOUR PERSONAL SPACE
        </p>

        <h1 className="mt-2 text-3xl font-bold text-[#353252]">
          Voice Journal
        </h1>

        <p className="mt-2 text-sm text-gray-400">
          Sometimes it feels easier to speak than to write.
          Take your time.
        </p>
      </div>

      <section className="rounded-3xl border border-[#efedf7] bg-white p-8 text-center shadow-sm">
        <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-[#eef0ff]">
          <Mic size={38} className="text-[#858fe8]" />
        </div>

        <h2 className="mt-6 text-xl font-bold text-[#45435f]">
          {status === "recording"
            ? "Listening to you..."
            : status === "paused"
            ? "Recording paused"
            : status === "ready"
            ? "Your recording is ready"
            : "Start when you're ready"}
        </h2>

        <p className="mt-2 text-sm text-gray-400">
          {status === "recording"
            ? "Speak naturally. You can pause whenever you need."
            : status === "paused"
            ? "Take a moment. Resume whenever you're ready."
            : "Your recording stays in this browser until you choose what to do with it."}
        </p>

        <div className="my-8">
          <p className="font-mono text-4xl font-semibold tracking-wider text-[#45435f]">
            {formatTime(recordingSeconds)}
          </p>

          <p className="mt-2 text-xs text-gray-400">
            RECORDING DURATION
          </p>
        </div>

        <div className="mb-5 text-left">
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Entry title (optional)
          </label>

          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={saving || !!experienceId}
            placeholder="Give this moment a title..."
            className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-indigo-400 disabled:bg-gray-50"
          />
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3">
          {status === "idle" && (
            <button
              onClick={startRecording}
              className="flex items-center gap-2 rounded-xl bg-[#858fe8] px-7 py-3 font-semibold text-white hover:bg-[#727edb]"
            >
              <Mic size={18} />
              Start recording
            </button>
          )}

          {status === "recording" && (
            <>
              <button
                onClick={pauseRecording}
                className="flex items-center gap-2 rounded-xl border border-[#e8e7f3] px-5 py-3 text-sm font-semibold text-[#55536f]"
              >
                <Pause size={17} />
                Pause
              </button>

              <button
                onClick={stopRecording}
                className="flex items-center gap-2 rounded-xl bg-red-500 px-5 py-3 text-sm font-semibold text-white hover:bg-red-600"
              >
                <Square size={16} />
                Stop
              </button>
            </>
          )}

          {status === "paused" && (
            <>
              <button
                onClick={resumeRecording}
                className="flex items-center gap-2 rounded-xl bg-[#858fe8] px-5 py-3 text-sm font-semibold text-white"
              >
                <Play size={17} />
                Resume
              </button>

              <button
                onClick={stopRecording}
                className="flex items-center gap-2 rounded-xl bg-red-500 px-5 py-3 text-sm font-semibold text-white"
              >
                <Square size={16} />
                Stop
              </button>
            </>
          )}
        </div>

        {audioUrl && (
          <div className="mt-8 space-y-4 rounded-2xl bg-[#f8f8ff] p-5 text-left">
            <div className="flex items-center gap-2">
              <AudioLines size={19} className="text-[#858fe8]" />
              <span className="text-sm font-semibold text-[#45435f]">
                Recording preview
              </span>
            </div>

            <audio controls src={audioUrl} className="w-full" />

            <button
              onClick={handleSaveEntry}
              disabled={saving || !recordedBlob || !!experienceId}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving ? (
                <>
                  <LoaderCircle size={18} className="animate-spin" />
                  {experienceId ? "Analyzing speech..." : "Saving entry..."}
                </>
              ) : experienceId ? (
                <>
                  <CheckCircle size={18} />
                  Entry saved
                </>
              ) : (
                "Save Voice Entry"
              )}
            </button>

            {saveError && (
              <p className="text-sm text-red-500">{saveError}</p>
            )}

            {analyzing && (
              <p className="text-sm text-indigo-600">
                Your voice entry is saved. Analyzing vocal expression...
              </p>
            )}

            {analysisError && (
              <div className="space-y-2">
                <p className="text-sm text-red-500">{analysisError}</p>

                <button
                  onClick={() => handleAnalyzeSpeech(experienceId)}
                  disabled={analyzing}
                  className="rounded-lg border border-indigo-200 px-4 py-2 text-sm font-medium text-indigo-600 disabled:opacity-50"
                >
                  Retry analysis
                </button>
              </div>
            )}

            {analysisResult && (
              <div className="rounded-xl border border-green-100 bg-green-50 p-4">
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle size={18} />
                  <span className="font-semibold">
                    Speech analysis complete
                  </span>
                </div>

                {analysisResult.predicted_emotion && (
                  <p className="mt-2 text-sm text-gray-700">
                    Suggested vocal emotion:{" "}
                    <strong className="capitalize">
                      {analysisResult.predicted_emotion}
                    </strong>
                  </p>
                )}

                <p className="mt-2 text-xs text-gray-500">
                  This is a model estimate of vocal expression, not a
                  definitive assessment of how you feel.
                </p>
              </div>
            )}

            {!experienceId && (
              <button
                onClick={discardRecording}
                disabled={saving}
                className="flex items-center gap-2 text-sm text-red-500 hover:text-red-600 disabled:opacity-50"
              >
                <RotateCcw size={15} />
                Discard and record again
              </button>
            )}
          </div>
        )}
      </section>

      {error && (
        <div className="flex items-start gap-3 rounded-xl bg-red-50 p-4 text-sm text-red-600">
          <AlertCircle size={18} className="mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      <p className="text-center text-xs leading-relaxed text-gray-400">
        Your voice is personal. Nothing is uploaded until you choose to
        save your recording. Saving creates your entry and starts
        temporary speech analysis.
      </p>
    </div>
  );
}
