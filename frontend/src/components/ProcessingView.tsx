import { Activity, Check, Cpu, Database, ScanSearch } from 'lucide-react'

export function ProcessingView({progress, uploadProgress, error, onReset}:{progress:number;uploadProgress:number;error:string;onReset:()=>void}) {
  const stages = [{at:0,icon:Database,label:'Video received'},{at:8,icon:ScanSearch,label:'Detecting & tracking'},{at:52,icon:Activity,label:'Modeling traffic flow'},{at:92,icon:Cpu,label:'Building forecast'}]
  return <main className="processing-page"><section className="processing-card">
    <div className="radar"><span/><span/><span/><i/></div>
    <span className="eyebrow">Analysis in progress</span><h1>{error ? 'Analysis interrupted' : 'Reading the rhythm of the road'}</h1>
    <p>{error || 'We’re detecting road users, reconstructing lane activity, and estimating the congestion trajectory.'}</p>
    {!error && <><div className="progress-readout"><strong>{Math.round(progress)}%</strong><span>{progress<2?`Uploading · ${uploadProgress}%`:'Processing video'}</span></div><div className="progress-track"><span style={{width:`${Math.max(progress,2)}%`}}/></div>
    <div className="stage-list">{stages.map(({at,icon:Icon,label})=><div className={progress>=at?'active':''} key={label}><span>{progress>at+20?<Check size={15}/>:<Icon size={15}/>}</span>{label}</div>)}</div></>}
    {error && <button className="secondary-btn" onClick={onReset}>Return to upload</button>}
  </section></main>
}
