export function Loading({ label = 'Cargando…' }: { label?: string }) { return <p className="feedback loading" role="status">{label}</p> }
