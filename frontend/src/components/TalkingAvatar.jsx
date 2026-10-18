import { useRef, useState } from "react";
import { TalkingAvatarView } from "@interviewflowai/talking-avatar/react";

export function TalkingAvatar() {
  const avatar = useRef(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const speak = (text) => {
    if (avatar.current) {
      setIsSpeaking(true);
      // Convert text to speech using Web Speech API
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'fr-FR';
      utterance.onend = () => setIsSpeaking(false);
      
      // Note: For full talking avatar lip-sync, you'd need to generate audio file
      // This is a simplified version with speech synthesis
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className="talking-avatar-container">
      <div style={{ width: "100%", height: 360, borderRadius: "12px", overflow: "hidden" }}>
        <TalkingAvatarView
          ref={avatar}
          avatarUrl="/avatar.glb"
          modelUrl="/sdk/viseme-model.bin"
          onError={(error) => console.error("Avatar error:", error)}
        />
      </div>
      <div className="avatar-controls">
        <button 
          onClick={() => speak("Bonjour! Je suis HERwell AI, votre assistant de bien-être.")}
          disabled={isSpeaking}
          className="avatar-btn"
        >
          {isSpeaking ? "Parle..." : "Tester l'avatar"}
        </button>
      </div>
    </div>
  );
}
