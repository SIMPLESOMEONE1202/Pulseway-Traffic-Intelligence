import type { Results, Status } from './types'

const API = import.meta.env.VITE_API_URL || '/api'
export const mediaUrl = (path: string) => `${API}${path}`

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, init)
  if (!response.ok) {
    const detail = await response.json().catch(() => ({detail: response.statusText}))
    throw new Error(detail.detail || 'Request failed')
  }
  return response.json()
}

export async function uploadVideo(file: File, onProgress: (value:number)=>void): Promise<{job_id:string}> {
  return new Promise((resolve, reject) => {
    const data = new FormData(); data.append('file', file)
    const xhr = new XMLHttpRequest(); xhr.open('POST', `${API}/upload`)
    xhr.upload.onprogress = event => event.lengthComputable && onProgress(Math.round(event.loaded / event.total * 100))
    xhr.onload = () => xhr.status >= 200 && xhr.status < 300 ? resolve(JSON.parse(xhr.responseText)) : reject(new Error(JSON.parse(xhr.responseText || '{}').detail || 'Upload failed'))
    xhr.onerror = () => reject(new Error('Could not reach the analysis server'))
    xhr.send(data)
  })
}
export const getStatus = (id:string) => request<Status>(`/jobs/${id}/status`)
export const getResults = (id:string) => request<Results>(`/jobs/${id}/results`)
