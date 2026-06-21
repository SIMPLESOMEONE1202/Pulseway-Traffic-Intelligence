export type Status = {job_id: string; status: 'queued'|'processing'|'done'|'failed'; progress: number; error?: string}
export type Lane = {lane: number; count: number; avg_speed_kmh: number}
export type Point = {timestamp_sec?: number; t_minutes?: number; score: number; predicted?: boolean}
export type Results = {
  job_id: string
  video_meta: {fps:number; frames_processed:number; duration_sec:number; resolution:string; avg_inference_ms:number; detector:string}
  vehicle_counts: Record<string, number>
  congestion: {current_score:number; current_level:string; observed:Point[]; predicted_trend:Point[]}
  lanes: Lane[]
  incidents: {track_id:number; type:string; timestamp_sec:number; lane:number}[]
  speed: {avg_kmh:number; calibration:string}
  signal_recommendation: {phase:string; green_time_sec:number; reason:string}
  media: {video_url:string; heatmap_url:string; bev_url:string; metrics_url:string}
}
