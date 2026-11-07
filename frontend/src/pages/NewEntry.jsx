
import { useState } from "react";
import { ArrowLeft, Save, Sparkles, RefreshCw } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const emotions = [
  "happy", "calm", "excited", "grateful",
  "sad", "anxious", "angry", "overwhelmed",
  "lonely", "confused", "frustrated", "hopeful",
  "embarrassed"
];

export default function NewEntry() {
  const navigate = useNavigate();

  const [selectedEmotions, setSelectedEmotions] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  const [form, setForm] = useState({
    title: "",
    occurred_at: new Date().toISOString().slice(0, 16),
    situation: "",
    thoughts: "",
    response: "",
    helped: ""
  });

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));

    // Previous analysis may no longer represent the edited text.
    setAnalysis(null);
    setAnalysisError("");
  };

  const toggleEmotion = (emotion) => {
    setSelectedEmotions(prev =>
      prev.includes(emotion)
        ? prev.filter(item => item !== emotion)
        : [...prev, emotion]
    );
  };

  // -----------------------------------------
  // AI TEXT EMOTION ANALYSIS
  // -----------------------------------------

  const handleAnalyzeText = async () => {
    const analysisText = [
      form.title,
      form.situation,
      form.thoughts,
      form.response,
      form.helped
    ]
      .filter(value => value?.trim())
      .join("\n\n");

    if (!analysisText.trim()) {
      setAnalysisError(
        "Write something about your experience first."
      );
      return;
    }

    try {
      setIsAnalyzing(true);
      setAnalysisError("");
      setAnalysis(null);

      const response = await api.post("/analysis/text", {
        text: analysisText,
        threshold: 0.30
      });

      setAnalysis(response.data);

    } catch (err) {
      setAnalysisError(
        err.response?.data?.detail ||
        "Could not analyse your writing. Please try again."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  // -----------------------------------------
  // SAVE JOURNAL ENTRY
  // -----------------------------------------

  const handleSubmit = async (e) => {
    e.preventDefault();

    setSaving(true);
    setError("");

    try {
      await api.post("/experiences/", {
        ...form,
        occurred_at: new Date(form.occurred_at).toISOString(),
        emotions: selectedEmotions
      });

      navigate("/journal");

    } catch (err) {
      setError(
        err.response?.data?.detail
          ? JSON.stringify(err.response.data.detail)
          : "Unable to save your entry. Please try again."
      );
    } finally {
      setSaving(false);
    }
  };

  // -----------------------------------------
  // REUSABLE TEXT FIELD
  // -----------------------------------------

  const Field = ({ label, value, onChange, placeholder }) => (
    <div className="space-y-2">
      <label className="text-sm font-semibold text-[#45435f]">
        {label}
      </label>

      <textarea
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        rows={4}
        className="w-full resize-y rounded-xl border border-[#eae9f5] bg-[#fcfcff] p-4 text-sm outline-none placeholder:text-gray-300 focus:border-[#9a9ff0]"
      />
    </div>
  );

  // -----------------------------------------
  // PAGE UI
  // -----------------------------------------

  return (
    <div className="mx-auto max-w-4xl space-y-7">

      {/* Back button */}

      <button
        type="button"
        onClick={() => navigate("/journal")}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-[#858fe8]"
      >
        <ArrowLeft size={17} />
        Back to journal
      </button>

      {/* Page heading */}

      <div>
        <p className="text-xs font-bold uppercase tracking-widest text-[#858fe8]">
          YOUR PERSONAL SPACE
        </p>

        <h1 className="mt-2 text-3xl font-bold text-[#353252]">
          Capture an experience.
        </h1>

        <p className="mt-2 text-sm text-gray-400">
          Take your time. There is no right or wrong way to express yourself.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* EXPERIENCE */}

        <section className="space-y-4 rounded-2xl border border-[#efedf7] bg-white p-7">

          <h2 className="font-bold text-[#45435f]">
            The experience
          </h2>

          <input
            required
            maxLength={200}
            value={form.title}
            onChange={e => updateField("title", e.target.value)}
            placeholder="Give this experience a title..."
            className="w-full rounded-xl border border-[#eae9f5] bg-[#fcfcff] px-4 py-3 text-sm outline-none focus:border-[#9a9ff0]"
          />

          <div className="space-y-2">
            <label className="text-sm font-semibold text-[#45435f]">
              When did this happen?
            </label>

            <input
              required
              type="datetime-local"
              value={form.occurred_at}
              onChange={e => updateField("occurred_at", e.target.value)}
              className="w-full rounded-xl border border-[#eae9f5] bg-[#fcfcff] px-4 py-3 text-sm outline-none"
            />
          </div>

          <Field
            label="What happened?"
            value={form.situation}
            onChange={e => updateField("situation", e.target.value)}
            placeholder="Describe the situation in your own words..."
          />

        </section>

        {/* USER REPORTED EMOTIONS */}

        <section className="space-y-5 rounded-2xl border border-[#efedf7] bg-white p-7">

          <div>
            <h2 className="font-bold text-[#45435f]">
              How did you feel?
            </h2>

            <p className="mt-1 text-xs text-gray-400">
              These are your own reported feelings. You can leave this blank.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {emotions.map(emotion => (
              <button
                key={emotion}
                type="button"
                onClick={() => toggleEmotion(emotion)}
                className={`rounded-full border px-4 py-2 text-sm capitalize transition ${
                  selectedEmotions.includes(emotion)
                    ? "border-[#858fe8] bg-[#eef0ff] font-semibold text-[#697de0]"
                    : "border-[#ecebf4] text-gray-500 hover:border-[#b9baf0]"
                }`}
              >
                {emotion}
              </button>
            ))}
          </div>

        </section>

        {/* REFLECTION */}

        <section className="space-y-6 rounded-2xl border border-[#efedf7] bg-white p-7">

          <h2 className="font-bold text-[#45435f]">
            Explore your experience
          </h2>

          <Field
            label="What was going through your mind?"
            value={form.thoughts}
            onChange={e => updateField("thoughts", e.target.value)}
            placeholder="What were you thinking?"
          />

          <Field
            label="How did you respond?"
            value={form.response}
            onChange={e => updateField("response", e.target.value)}
            placeholder="What did you do or how did you react?"
          />

          <Field
            label="What helped you?"
            value={form.helped}
            onChange={e => updateField("helped", e.target.value)}
            placeholder="Did anything make the situation easier?"
          />

        </section>

        {/* AI EMOTION ANALYSIS */}

        <section className="space-y-5 rounded-2xl border border-[#dfe2ff] bg-gradient-to-br from-[#f7f7ff] to-[#f0f2ff] p-7">

          <div className="flex items-start gap-3">

            <div className="rounded-xl bg-white p-3 text-[#858fe8] shadow-sm">
              <Sparkles size={21} />
            </div>

            <div>
              <h2 className="font-bold text-[#45435f]">
                Understand your emotions
              </h2>

              <p className="mt-1 text-sm leading-relaxed text-gray-500">
                Explore possible emotional patterns in your writing
                with AI-powered analysis.
              </p>
            </div>

          </div>

          <button
            type="button"
            onClick={handleAnalyzeText}
            disabled={isAnalyzing}
            className="flex items-center justify-center gap-2 rounded-xl bg-[#858fe8] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#727edb] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                Analysing your writing...
              </>
            ) : (
              <>
                <Sparkles size={16} />
                {analysis ? "Analyse again" : "Analyse my writing"}
              </>
            )}
          </button>

          {analysisError && (
            <p className="rounded-xl bg-red-50 p-3 text-sm text-red-600">
              {analysisError}
            </p>
          )}

          {/* ANALYSIS RESULTS */}

          {analysis && (
            <div className="space-y-4 rounded-xl border border-[#e8e9fb] bg-white p-5">

              <div>
                <h3 className="font-semibold text-[#45435f]">
                  Possible emotions detected
                </h3>

                <p className="mt-1 text-xs text-gray-400">
                  AI estimates based on your writing
                </p>
              </div>

              {analysis.suggested_emotions.length > 0 ? (

                <div className="flex flex-wrap gap-2">

                  {analysis.suggested_emotions.map(item => (
                    <div
                      key={item.emotion}
                      className="rounded-xl border border-[#e7e8fb] bg-[#f8f8ff] px-3 py-2"
                    >
                      <span className="text-sm font-semibold capitalize text-[#45435f]">
                        {item.emotion}
                      </span>

                      <span className="ml-2 text-xs font-medium text-[#858fe8]">
                        {(item.score * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}

                </div>

              ) : (

                <p className="text-sm text-gray-500">
                  No suggestions crossed the current confidence threshold.
                </p>

              )}

              <p className="border-t border-[#f0eff7] pt-3 text-xs leading-relaxed text-gray-400">
                These are model-generated estimates, not facts about
                how you feel. You are the best judge of your own experience.
                Your selections above remain separate from these suggestions.
              </p>

            </div>
          )}

        </section>

        {/* SAVE ERROR */}

        {error && (
          <p className="rounded-xl bg-red-50 p-4 text-sm text-red-600">
            {error}
          </p>
        )}

        {/* SAVE BUTTON */}

        <div className="flex justify-end">

          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 rounded-xl bg-[#858fe8] px-6 py-3 text-sm font-semibold text-white hover:bg-[#727edb] disabled:opacity-60"
          >
            {saving ? (
              "Saving..."
            ) : (
              <>
                <Save size={17} />
                Save experience
              </>
            )}
          </button>

        </div>

      </form>
    </div>
  );
}
