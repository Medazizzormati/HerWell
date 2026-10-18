import React, { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, OrbitControls } from "@react-three/drei";
import { Mic, MicOff, Send, Volume2, VolumeX, Sparkles, LoaderCircle } from "lucide-react";
import "./herwell-voice.css";

const API = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

function AvatarFace({ speaking, level }) {
  const mouth = useRef();
  const head = useRef();
  useFrame((state, delta) => {
    if (head.current) head.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.4) * 0.07;
    if (mouth.current) {
      const target = speaking ? 0.08 + Math.min(0.85, level * 1.4) : 0.07;
      mouth.current.scale.y += (target - mouth.current.scale.y) * Math.min(1, delta * 13);
    }
  });
  return <group ref={head} position={[0, -0.1, 0]}>
    <mesh position={[0, -0.68, -0.05]}><capsuleGeometry args={[0.42, 0.58, 8, 16]} /><meshStandardMaterial color="#d7aa9e" /></mesh>
    <mesh position={[0, 0.1, 0]}><sphereGeometry args={[0.8, 40, 40]} /><meshStandardMaterial color="#e7bfb1" roughness={0.8} /></mesh>
    <mesh position={[0, 0.48, -0.03]} scale={[1.03, 0.72, 1]}><sphereGeometry args={[0.79, 40, 32]} /><meshStandardMaterial color="#3d2945" roughness={0.9} /></mesh>
    <mesh position={[-0.29, 0.17, 0.68]}><sphereGeometry args={[0.09, 20, 20]} /><meshStandardMaterial color="#302333" /></mesh>
    <mesh position={[0.29, 0.17, 0.68]}><sphereGeometry args={[0.09, 20, 20]} /><meshStandardMaterial color="#302333" /></mesh>
    <mesh position={[0, -0.02, 0.77]}><sphereGeometry args={[0.065, 20, 20]} /><meshStandardMaterial color="#c99183" /></mesh>
    <mesh ref={mouth} position={[0, -0.28, 0.735]} scale={[0.18, 0.07, 0.035]}><sphereGeometry args={[1, 24, 16]} /><meshStandardMaterial color="#582c3c" /></mesh>
  </group>;
}

function AvatarScene({ speaking, level }) {
  return <Canvas camera={{ position: [0, 0.12, 4], fov: 36 }} dpr={[1, 1.5]}>
    <ambientLight intensity={1.5} /><directionalLight position={[3, 4, 5]} intensity={2} />
    <Suspense fallback={null}><AvatarFace speaking={speaking} level={level} /><Environment preset="studio" /></Suspense>
    <OrbitControls enablePan={false} enableZoom={false} minPolarAngle={1.2} maxPolarAngle={1.9} />
  </Canvas>;
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

  useEffect(() => () => {
    stream.current?.getTracks().forEach(t => t.stop());
    if (raf.current) cancelAnimationFrame(raf.current);
    audio.current?.pause();
    audioContext.current?.close?.();
  }, []);

  const playAudio = useCallback(async (blob) => {
    if (muted) return;
    audio.current?.pause();
    const player = new Audio(URL.createObjectURL(blob));
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
    player.onended = () => { setStatus("idle"); setLevel(0); URL.revokeObjectURL(player.src); };
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
        <div className="hw-canvas"><AvatarScene speaking={speaking} level={level} /></div>
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
