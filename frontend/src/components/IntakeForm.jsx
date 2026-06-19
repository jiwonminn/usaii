import { useState } from "react";

const PROMPTS = [
  "I have a nursing degree from the Philippines that isn't recognized here yet...",
  "I got into law school but also have a full-time offer at a bank...",
  "My partner wants to move to Calgary for a job but I'd have to start over...",
];

export default function IntakeForm({ onSubmit, isLoading }) {
  const [text, setText] = useState("");
  const [placeholderIndex] = useState(() => Math.floor(Math.random() * PROMPTS.length));

  function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim() || isLoading) return;
    onSubmit(text.trim());
  }

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;

  return (
    <section className="intake">
      <h1 className="intake__title">What are you trying to decide?</h1>
      <p className="intake__sub">
        Describe your situation the way you'd explain it to a friend. Include what's at
        stake, what's pulling you in each direction, and anything that limits your options —
        savings, time, people depending on you.
      </p>

      <form onSubmit={handleSubmit} className="intake__form">
        <textarea
          className="intake__textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={PROMPTS[placeholderIndex]}
          rows={7}
          disabled={isLoading}
          aria-label="Describe your decision"
        />
        <div className="intake__footer">
          <span className="intake__count">{wordCount} words</span>
          <button
            type="submit"
            className="intake__submit"
            disabled={!text.trim() || isLoading}
          >
            {isLoading ? "Thinking it through…" : "Map my paths"}
          </button>
        </div>
      </form>
    </section>
  );
}
