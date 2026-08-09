import { useEffect, useRef, useState } from 'react';
import { listAgents, sendMessage } from '../api/client.js';

export default function ChatPage() {
  const [messages, setMessages] = useState([]); // { role: 'user' | 'assistant', content }
  // { stage, agent, description }[] — whichever stages the backend actually has.
  const [agents, setAgents] = useState([]);
  const [stage, setStage] = useState('');
  const [threadId, setThreadId] = useState(null);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const endRef = useRef(null);

  useEffect(() => {
    listAgents()
      .then((found) => {
        setAgents(found);
        if (found.length > 0) setStage(found[0].stage);
      })
      .catch((err) => setError(err.message));
  }, []);

  // Keep the latest message in view as the conversation grows.
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const handleSend = async (e) => {
    e.preventDefault();
    const text = input.trim();
    const selected = agents.find((a) => a.stage === stage);
    if (!text || sending) return;
    if (!selected) {
      setError('No agent available to send to.');
      return;
    }

    setError('');
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setSending(true);
    try {
      // Passing the existing threadId continues the server-side conversation;
      // the first call (threadId === null) starts a new one and returns its id.
      const res = await sendMessage(text, threadId, selected.stage, selected.agent);
      setThreadId(res.thread_id);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.response }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  };

  const startNewChat = () => {
    setThreadId(null);
    setMessages([]);
    setError('');
  };

  return (
    <div className="chat-screen">
      {/* Brand, role and log out now live in AppShell's header; this toolbar
          keeps only the controls that belong to the conversation itself. */}
      <div className="chat-toolbar">
        <label className="stage-picker">
          <span className="stage-label">Agent</span>
          <select
            className="stage-select"
            value={stage}
            onChange={(e) => setStage(e.target.value)}
            disabled={sending || agents.length === 0}
          >
            {agents.map((a) => (
              <option key={a.stage} value={a.stage} title={a.description}>
                {a.stage} · {a.agent}
              </option>
            ))}
          </select>
        </label>
        <button className="ghost-btn" onClick={startNewChat} disabled={sending}>
          New chat
        </button>
      </div>

      <main className="chat-body">
        {messages.length === 0 && !sending && (
          <div className="empty-state">
            <h2>Ask Otto anything</h2>
            <p>Your messages run through the research assistant agent.</p>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`bubble-row ${m.role}`}>
            <div className={`bubble ${m.role}`}>{m.content}</div>
          </div>
        ))}

        {sending && (
          <div className="bubble-row assistant">
            <div className="bubble assistant typing">
              <span /> <span /> <span />
            </div>
          </div>
        )}

        <div ref={endRef} />
      </main>

      {error && <p className="error-banner chat-error">{error}</p>}

      <form className="chat-input-bar" onSubmit={handleSend}>
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend(e);
            }
          }}
          placeholder="Type a message…  (Enter to send, Shift+Enter for newline)"
          rows={1}
        />
        <button className="primary-btn send-btn" type="submit" disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
