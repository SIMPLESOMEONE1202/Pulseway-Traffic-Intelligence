import { useEffect, useState } from 'react'
import { getResults, getStatus, uploadVideo } from './api'
import { Dashboard } from './components/Dashboard'
import { ProcessingView } from './components/ProcessingView'
import { UploadView } from './components/UploadView'
import type { Results } from './types'

type Screen='upload'|'processing'|'results'
export default function App(){
  const [screen,setScreen]=useState<Screen>('upload'),[job,setJob]=useState(''),[progress,setProgress]=useState(0),[uploadProgress,setUploadProgress]=useState(0),[error,setError]=useState(''),[results,setResults]=useState<Results|null>(null)
  const reset=()=>{setScreen('upload');setJob('');setProgress(0);setUploadProgress(0);setError('');setResults(null)}
  const start=async(file:File)=>{setScreen('processing');setError('');try{const created=await uploadVideo(file,setUploadProgress);setJob(created.job_id);setProgress(1)}catch(e){setError(e instanceof Error?e.message:'Upload failed')}}
  useEffect(()=>{if(!job||screen!=='processing'||error)return;const timer=setInterval(async()=>{try{const status=await getStatus(job);setProgress(status.progress);if(status.status==='failed'){setError(status.error||'Analysis failed');clearInterval(timer)}if(status.status==='done'){const data=await getResults(job);setResults(data);setScreen('results');clearInterval(timer)}}catch(e){setError(e instanceof Error?e.message:'Connection lost');clearInterval(timer)}},1200);return()=>clearInterval(timer)},[job,screen,error])
  return <div className="app-shell"><nav className="site-nav"><button className="brand" onClick={reset}><span className="brand-mark"><i/><i/><i/></span><span>PULSEWAY<small>TRAFFIC INTELLIGENCE</small></span></button><div className="system-state"><span/> ANALYTICS NODE ONLINE</div></nav>{screen==='upload'&&<UploadView onStart={start}/>} {screen==='processing'&&<ProcessingView progress={progress} uploadProgress={uploadProgress} error={error} onReset={reset}/>} {screen==='results'&&results&&<Dashboard data={results} onReset={reset}/>}</div>
}
