import React, { useCallback, useEffect, useRef, useState } from "react";
import { TalkingAvatarView } from "@interviewflowai/talking-avatar/react";
import { Mic, MicOff, Send, Volume2, VolumeX, Sparkles, LoaderCircle } from "lucide-react";
import "./herwell-voice.css";

const API = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

function RealisticAvatar({ speaking, avatarRef }) {
  return (
    <div style={{ width: "100%", height: 360, borderRadius: "12px", overflow: "hidden" }}>
      <TalkingAvatarView
        ref={avatarRef}
        avatarUrl="/avatar.glb"
        modelUrl="/sdk/viseme-model.bin"
        onError={(error) => console.error("Avatar error:", error)}
      />
    </div>
  );
}

export default function HerwellVoiceAssistant() {
  const [message, setMessage] = useState("");
  const [transcript, setTranscript] = useState("");
  const [answer, setAnswer] = useState("Bonjour, je suis HERwell. Tu peux me parler ou écrire ta question.");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [muted, setMuted] = useState(false);
  const [level, setLevel] = useState(0);
  const recorder = useRef(null), stream = useRef(null), chunks = useRef([]);
  const audio = useRef(null), audioContext = useRef(null), analyser = useRef(null), raf = useRef(null);
  const avatar = useRef(null);

  useEffect(() => () => {
    stream.current?.getTracks().forEach(t => t.stop());
    if (raf.current) cancelAnimationFrame(raf.current);
    audio.current?.pause();
    audioContext.current?.close?.();
  }, []);

  const playAudio = useCallback(async (blob) => {
    if (muted) return;
    audio.current?.pause();
    
    // Create audio URL for avatar
    const audioUrl = URL.createObjectURL(blob);
    
    // Make avatar speak with the audio first
    if (avatar.current) {
      try {
        await avatar.current.speak(audioUrl);
      } catch (e) {
        console.log("Avatar speaking error:", e);
        // Fall back to normal audio playback
      }
    }
    
    const player = new Audio(audioUrl);
    audio.current = player;
    
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      const ctx = new Ctx(); audioContext.current = ctx;
      const node = ctx.createMediaElementSource(player);
      const meter = ctx.createAnalyser(); meter.fftSize = 256;
      node.connect(meter); meter.connect(ctx.destination); analyser.current = meter;
      const values = new Uint8Array(meter.frequencyBinCount);
      const tick = () => {
        if (player.paused) { setLevel(0); return; }
        meter.getByteTimeDomainData(values);
        let sum = 0;
        for (const v of values) { const n = (v - 128) / 128; sum += n * n; }
        setLevel(Math.min(1, Math.sqrt(sum / values.length) * 4));
        raf.current = requestAnimationFrame(tick);
      };
      player.onplay = () => { ctx.resume(); tick(); };
    } catch { /* Audio can still play if analysis is unavailable. */ }
    player.onended = () => { setStatus("idle"); setLevel(0); URL.revokeObjectURL(audioUrl); };
    player.onerror = () => { setStatus("idle"); setError("Impossible de lire l'audio."); };
    setStatus("speaking");
    await player.play();
  }, [muted]);

  const send = useCallback(async (value = message) => {
    const clean = value.trim(); if (!clean) return;
    setError(""); setTranscript(clean); setMessage(""); setStatus("thinking");
    try {
      const res = await fetch(`${API}/api/voice/chat`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: clean, session_id: "herwell-web-session" })
      });
      if (!res.ok) { const data = await res.json().catch(() => ({})); throw new Error(data.detail || `Erreur HTTP ${res.status}`); }
      const spoken = decodeURIComponent(res.headers.get("X-Herwell-Answer") || "");
      if (spoken) setAnswer(spoken);
      await playAudio(await res.blob());
    } catch (e) { setStatus("idle"); setError(e.message || "Connexion au backend impossible."); }
  }, [message, playAudio]);

  const startRecording = async () => {
    setError("");
    try {
      const media = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.current = media; chunks.current = [];
      const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "";
      const rec = new MediaRecorder(media, mime ? { mimeType: mime } : undefined); recorder.current = rec;
      rec.ondataavailable = e => { if (e.data.size) chunks.current.push(e.data); };
      rec.onstop = async () => {
        media.getTracks().forEach(t => t.stop());
        setStatus("transcribing");
        try {
          const form = new FormData();
          form.append("file", new Blob(chunks.current, { type: rec.mimeType || "audio/webm" }), "question.webm");
          const res = await fetch(`${API}/api/voice/transcribe`, { method: "POST", body: form });
          const data = await res.json(); if (!res.ok) throw new Error(data.detail || "Transcription impossible.");
          setMessage(data.text || ""); setTranscript(data.text || ""); setStatus("idle");
        } catch (e) { setStatus("idle"); setError(e.message || "Erreur de transcription."); }
      };
      rec.start(); setStatus("listening");
    } catch (e) { setStatus("idle"); setError(e.message || "Microphone inaccessible."); }
  };

  const stopRecording = () => { if (recorder.current?.state === "recording") recorder.current.stop(); };
  const busy = ["thinking", "transcribing"].includes(status);
  const speaking = status === "speaking";

  return <section className="hw-shell">
    <header className="hw-header"><div className="hw-logo"><Sparkles size={19} /></div>
      <div><small>HERWELL AI</small><h1>Your private wellness companion</h1></div>
      <span className="hw-local"><i /> Local AI</span>
    </header>
    <div className="hw-layout">
      <div className={`hw-avatar ${speaking ? "speaking" : ""}`}>
        <div className="hw-label">● PRIVATE SESSION · LOCAL MODE</div>
        <div className="hw-canvas"><RealisticAvatar speaking={speaking} avatarRef={avatar} /></div>
        <div className="hw-caption"><b>HERwell</b><span>{status === "listening" ? "I'm listening…" : status === "transcribing" ? "Understanding your voice…" : status === "thinking" ? "Thinking carefully…" : speaking ? "Speaking with you…" : "Here for you, whenever you're ready."}</span></div>
      </div>
      <div className="hw-chat">
        <small>LET'S TALK</small><h2>A safe space to talk</h2>
        <div className="hw-answer"><b>HERWELL</b><p>{answer}</p></div>
        {transcript && <div className="hw-transcript"><b>YOU SAID</b><p>{transcript}</p></div>}
        {error && <div className="hw-error" role="alert">{error}</div>}
        <form className="hw-input" onSubmit={e => { e.preventDefault(); send(); }}>
          <input value={message} onChange={e => setMessage(e.target.value)} placeholder="Write what's on your mind…" disabled={busy || status === "listening"} />
          <button type="submit" disabled={!message.trim() || busy} aria-label="Send"><Send size={17} /></button>
        </form>
        <div className="hw-controls">
          {status === "listening" ? <button className="hw-mic recording" onClick={stopRecording}><MicOff size={18} /> Stop recording</button>
            : <button className="hw-mic" onClick={startRecording} disabled={busy || speaking}><Mic size={18} /> {busy ? (status === "transcribing" ? "Transcribing…" : "Thinking…") : "Talk to HERwell"}</button>}
          <button className="hw-volume" onClick={() => { setMuted(v => !v); if (!muted) audio.current?.pause(); }} aria-label="Mute audio">{muted ? <VolumeX size={18} /> : <Volume2 size={18} />}</button>
          {busy && <LoaderCircle className="hw-spin" size={18} />}
        </div>
        <p className="hw-disclaimer">Supportive information only — not a medical diagnosis or emergency service.</p>
      </div>
    </div>
    <footer className="hw-footer"><span>● Private by design</span><span>Local models · No paid voice API</span></footer>
  </section>;
}
