import { useRef, useState } from 'react'
import { ArrowRight, FileVideo, ShieldCheck, Sparkles, UploadCloud, X } from 'lucide-react'

const LIMIT = 500 * 1024 * 1024
export function UploadView({onStart}:{onStart:(file:File)=>void}) {
  const [file, setFile] = useState<File|null>(null), [dragging,setDragging] = useState(false), [error,setError] = useState('')
  const input = useRef<HTMLInputElement>(null)
  const accept = (candidate?:File) => {
    setError(''); if (!candidate) return
    if (!candidate.type.startsWith('video/') && !/\.(mp4|avi|mov|mkv|webm|m4v)$/i.test(candidate.name)) return setError('Choose a supported video file.')
    if (candidate.size > LIMIT) return setError('That video exceeds the 500 MB limit.')
    setFile(candidate)
  }
  return <main className="upload-page">
    <div className="hero-copy">
      <div className="kicker"><span/> Computer vision for moving cities</div>
      <h1>See the traffic.<br/><em>Shape what happens next.</em></h1>
      <p>Turn ordinary road footage into decision-ready intelligence—vehicle flows, lane pressure, incidents, and a short-horizon congestion forecast.</p>
      <div className="feature-row">
        <span><Sparkles size={15}/> Explainable prediction</span><span><ShieldCheck size={15}/> Privacy filtered</span><span><FileVideo size={15}/> Any road footage</span>
      </div>
    </div>
    <section className="upload-shell">
      <div className="upload-heading"><div><span className="step">01</span><h2>Upload footage</h2></div><span className="secure"><ShieldCheck size={14}/> Local processing</span></div>
      <button className={`dropzone ${dragging?'dragging':''}`} onClick={()=>input.current?.click()} onDragOver={e=>{e.preventDefault();setDragging(true)}} onDragLeave={()=>setDragging(false)} onDrop={e=>{e.preventDefault();setDragging(false);accept(e.dataTransfer.files[0])}}>
        <input ref={input} hidden type="file" accept="video/*,.mkv" onChange={e=>accept(e.target.files?.[0])}/>
        <span className="upload-orbit"><UploadCloud size={28}/></span><strong>Drop traffic footage here</strong><small>or click to choose a file</small><span className="file-hint">MP4 · MOV · AVI · MKV · WEBM  /  MAX 500 MB</span>
      </button>
      {file && <div className="file-pill"><span><FileVideo size={18}/></span><div><strong>{file.name}</strong><small>{(file.size/1048576).toFixed(1)} MB · Ready to analyze</small></div><button aria-label="Remove file" onClick={()=>setFile(null)}><X size={17}/></button></div>}
      {error && <p className="form-error">{error}</p>}
      <button className="primary-btn" disabled={!file} onClick={()=>file&&onStart(file)}>Start traffic analysis <ArrowRight size={18}/></button>
      <p className="privacy-note">Footage stays on your configured analysis server. Detected pedestrian head regions are blurred in generated media.</p>
    </section>
  </main>
}
