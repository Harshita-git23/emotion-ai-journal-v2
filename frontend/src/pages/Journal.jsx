
import { useEffect, useState } from "react";
import { Plus, BookHeart, CalendarDays, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Journal() {
  const navigate = useNavigate();

  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchEntries = async () => {
    try {
      const response = await api.get("/experiences/");
      setEntries(response.data);
    } catch (err) {
      setError("Unable to load your journal entries.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  const deleteEntry = async (id) => {
    if (!window.confirm("Are you sure you want to delete this experience?")) {
      return;
    }

    try {
      await api.delete(`/experiences/${id}`);
      setEntries(prev => prev.filter(entry => entry.id !== id));
    } catch {
      setError("Unable to delete this experience.");
    }
  };

  return (
    <div className="space-y-7">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-[#858fe8]">
            YOUR EXPERIENCES
          </p>
          <h1 className="mt-2 text-3xl font-bold text-[#353252]">
            My Journal
          </h1>
          <p className="mt-2 text-sm text-gray-400">
            A collection of moments, thoughts and reflections.
          </p>
        </div>

        <button
          onClick={() => navigate("/new-entry")}
          className="flex items-center gap-2 rounded-xl bg-[#858fe8] px-5 py-3 text-sm font-semibold text-white hover:bg-[#727edb]"
        >
          <Plus size={18} /> New Entry
        </button>
      </div>

      {error && (
        <p className="rounded-xl bg-red-50 p-4 text-sm text-red-600">
          {error}
        </p>
      )}

      {loading ? (
        <p className="py-12 text-center text-sm text-gray-400">
          Loading your experiences...
        </p>
      ) : entries.length === 0 ? (
        <div className="rounded-2xl border border-[#efedf7] bg-white px-6 py-16 text-center">
          <BookHeart className="mx-auto mb-4 text-[#aaa9e9]" size={35} />
          <h2 className="font-semibold text-[#45435f]">
            Your journal starts here.
          </h2>
          <p className="mt-2 text-sm text-gray-400">
            Record your first experience whenever you're ready.
          </p>
          <button
            onClick={() => navigate("/new-entry")}
            className="mt-6 rounded-xl bg-[#858fe8] px-5 py-3 text-sm font-semibold text-white"
          >
            Write your first entry
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {entries.map(entry => (
            <article
              key={entry.id}
              className="rounded-2xl border border-[#efedf7] bg-white p-6 shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-lg font-bold text-[#353252]">
                    {entry.title}
                  </h2>

                  <p className="mt-2 flex items-center gap-2 text-xs text-gray-400">
                    <CalendarDays size={14} />
                    {new Date(entry.occurred_at).toLocaleString()}
                  </p>
                </div>

                <button
                  onClick={() => deleteEntry(entry.id)}
                  title="Delete entry"
                  className="rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-500"
                >
                  <Trash2 size={17} />
                </button>
              </div>

              <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-gray-600">
                {entry.situation}
              </p>

              {entry.emotions?.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {entry.emotions.map(emotion => (
                    <span
                      key={emotion.emotion}
                      className="rounded-full bg-[#eef0ff] px-3 py-1 text-xs capitalize text-[#697de0]"
                    >
                      {emotion.emotion}
                    </span>
                  ))}
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
