"use client";
import { useState, useRef, useCallback } from "react";
import { Upload, Loader2, Download, CheckCircle, AlertCircle, ChevronDown } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const LANGUAGES = [
  { value: "darija", label: "Darija دارجة" },
  { value: "french", label: "Français" },
  { value: "arabic", label: "Arabic فصحى" },
  { value: "english", label: "English" },
];

type Script = { hook: string; body: string; cta: string; angle: string };
type Result = {
  product: { name: string; niche: string; description: string };
  scripts: Record<string, Script>;
  reels: Record<string, string>;
};

export default function Home() {
  const [inviteCode, setInviteCode] = useState("");
  const [codeVerified, setCodeVerified] = useState(false);
  const [codeError, setCodeError] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [language, setLanguage] = useState("darija");
  const [scriptMode, setScriptMode] = useState<"ai" | "manual">("ai");
  const [manualScript, setManualScript] = useState("");
  const [running, setRunning] = useState(false);
  const [steps, setSteps] = useState<string[]>([]);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const verifyCode = async () => {
    setCodeError("");
    try {
      const res = await fetch(`${API}/api/verify-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: inviteCode }),
      });
      if (res.ok) setCodeVerified(true);
      else setCodeError("Code invalide ❌");
    } catch {
      setCodeError("Erreur connexion serveur ❌");
    }
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
    }
  }, []);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const startPipeline = async () => {
    if (!image || !codeVerified) return;
    if (scriptMode === "manual" && !manualScript.trim()) return;
    setRunning(true);
    setSteps([]);
    setResult(null);
    setError("");

    const form = new FormData();
    form.append("image", image);
    form.append("language", language);
    form.append("invite_code", inviteCode);
    if (scriptMode === "manual") {
      form.append("manual_script", manualScript.trim());
    }

    const res = await fetch(`${API}/api/start`, { method: "POST", body: form });
    if (!res.ok) {
      setError("Erreur démarrage pipeline");
      setRunning(false);
      return;
    }
    const { job_id } = await res.json();

    let seenSteps = 0;
    const poll = async () => {
      try {
        const r = await fetch(`${API}/api/status/${job_id}`);
        if (!r.ok) { setError("Erreur connexion serveur"); setRunning(false); return; }
        const data = await r.json();
        if (data.steps && data.steps.length > seenSteps) {
          setSteps((prev) => [...prev, ...data.steps.slice(seenSteps)]);
          seenSteps = data.steps.length;
        }
        if (data.status === "done") {
          setResult(data.result);
          setRunning(false);
        } else if (data.status === "error") {
          setError(data.error || "Erreur pipeline");
          setRunning(false);
        } else {
          setTimeout(poll, 3000);
        }
      } catch {
        setTimeout(poll, 5000);
      }
    };
    poll();
  };

  if (!codeVerified) {
    return (
      <main className="min-h-screen bg-black flex items-center justify-center p-4">
        <div className="w-full max-w-sm">
          <h1 className="text-3xl font-bold text-white text-center mb-2">ReelGen</h1>
          <p className="text-zinc-400 text-center mb-8 text-sm">Image → 3 reels prêts à poster</p>
          <div className="bg-zinc-900 rounded-2xl p-6 border border-zinc-800">
            <label className="text-zinc-300 text-sm font-medium mb-2 block">Code d&apos;invitation</label>
            <input
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && verifyCode()}
              placeholder="XXXX-XXXX"
              className="w-full bg-zinc-800 text-white rounded-xl px-4 py-3 text-sm outline-none border border-zinc-700 focus:border-violet-500 transition mb-3"
            />
            {codeError && <p className="text-red-400 text-xs mb-3">{codeError}</p>}
            <button
              onClick={verifyCode}
              className="w-full bg-violet-600 hover:bg-violet-500 text-white font-semibold py-3 rounded-xl transition"
            >
              Entrer
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-black text-white p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-1">ReelGen <span className="text-violet-400">✦</span></h1>
          <p className="text-zinc-400 text-sm">Photo du produit → 3 reels 30s prêts à poster</p>
        </div>

        {/* Image Upload */}
        <div
          onDrop={onDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileRef.current?.click()}
          className="relative border-2 border-dashed border-zinc-700 hover:border-violet-500 rounded-2xl p-8 text-center cursor-pointer transition mb-4 min-h-[200px] flex items-center justify-center"
        >
          <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={onFileChange} />
          {preview ? (
            <img src={preview} alt="product" className="max-h-64 rounded-xl object-contain mx-auto" />
          ) : (
            <div>
              <Upload className="mx-auto mb-3 text-zinc-500" size={36} />
              <p className="text-zinc-400 text-sm">Glisse l&apos;image ici ou clique pour choisir</p>
            </div>
          )}
        </div>

        {/* Language selector */}
        <div className="relative mb-4">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full appearance-none bg-zinc-900 border border-zinc-700 text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-violet-500 transition cursor-pointer"
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-4 top-3.5 text-zinc-400 pointer-events-none" size={16} />
        </div>

        {/* Script Mode Toggle */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 mb-4">
          <div className="flex gap-2 mb-3">
            <button
              onClick={() => setScriptMode("ai")}
              className={`flex-1 py-2 rounded-xl text-sm font-semibold transition ${
                scriptMode === "ai"
                  ? "bg-violet-600 text-white"
                  : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
              }`}
            >
              🤖 Script IA
            </button>
            <button
              onClick={() => setScriptMode("manual")}
              className={`flex-1 py-2 rounded-xl text-sm font-semibold transition ${
                scriptMode === "manual"
                  ? "bg-violet-600 text-white"
                  : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
              }`}
            >
              ✍️ Script Manuel
            </button>
          </div>

          {scriptMode === "ai" && (
            <p className="text-zinc-500 text-xs">L&apos;IA génère 3 scripts A/B/C automatiquement depuis la photo.</p>
          )}

          {scriptMode === "manual" && (
            <textarea
              value={manualScript}
              onChange={(e) => setManualScript(e.target.value)}
              placeholder="Écris ton script ici... (utilisé pour les 3 reels)"
              rows={5}
              className="w-full bg-zinc-800 text-white rounded-xl px-4 py-3 text-sm outline-none border border-zinc-700 focus:border-violet-500 transition resize-none"
            />
          )}
        </div>

        {/* Launch button */}
        <button
          onClick={startPipeline}
          disabled={!image || running || (scriptMode === "manual" && !manualScript.trim())}
          className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-xl transition flex items-center justify-center gap-2 text-base mb-6"
        >
          {running ? (
            <><Loader2 size={18} className="animate-spin" /> Pipeline en cours...</>
          ) : (
            "🚀 Lancer le pipeline"
          )}
        </button>

        {/* Progress log */}
        {steps.length > 0 && (
          <div className="bg-zinc-900 rounded-2xl p-4 border border-zinc-800 mb-6 font-mono text-sm space-y-1 max-h-64 overflow-y-auto">
            {steps.map((s, i) => (
              <div key={i} className="text-zinc-300">{s}</div>
            ))}
            {running && <div className="text-violet-400 animate-pulse">⏳ Traitement...</div>}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-2xl p-4 mb-6 flex gap-2 text-red-300 text-sm">
            <AlertCircle size={16} className="shrink-0 mt-0.5" />
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="space-y-4">
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle size={16} className="text-green-400" />
                <span className="font-semibold">{result.product.name}</span>
              </div>
              <p className="text-zinc-400 text-sm">{result.product.description}</p>
            </div>

            {(["A", "B", "C"] as const).map((v) => {
              const s = result.scripts[v];
              return (
                <div key={v} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-bold text-violet-400">Script {v}</span>
                    <span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-1 rounded-full">{s.angle}</span>
                  </div>
                  <p className="text-xs text-zinc-500 mb-1">HOOK</p>
                  <p className="text-sm text-zinc-200 mb-2">{s.hook}</p>
                  <p className="text-xs text-zinc-500 mb-1">BODY</p>
                  <p className="text-sm text-zinc-300 mb-2">{s.body}</p>
                  <p className="text-xs text-zinc-500 mb-1">CTA</p>
                  <p className="text-sm text-zinc-200">{s.cta}</p>
                </div>
              );
            })}

            <div className="grid grid-cols-3 gap-3">
              {(["A", "B", "C"] as const).map((v) => (
                <a
                  key={v}
                  href={`${API}${result.reels[v]}`}
                  download={`reel_${v}.mp4`}
                  className="flex flex-col items-center justify-center gap-2 bg-violet-600 hover:bg-violet-500 text-white rounded-2xl py-4 transition font-semibold text-sm"
                >
                  <Download size={20} />
                  Reel {v}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
