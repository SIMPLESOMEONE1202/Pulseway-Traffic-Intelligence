import type { LucideIcon } from 'lucide-react'

export function MetricCard({icon:Icon, label, value, detail, tone='lime'}:{icon:LucideIcon;label:string;value:string;detail:string;tone?:string}) {
  return <article className={`metric-card tone-${tone}`}>
    <div className="metric-top"><span className="metric-icon"><Icon size={17}/></span><span className="eyebrow">{label}</span></div>
    <strong>{value}</strong><span className="metric-detail">{detail}</span>
  </article>
}
