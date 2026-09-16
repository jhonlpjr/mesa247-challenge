import { Link } from 'react-router-dom'
import type { PropsWithChildren } from 'react'

export function Layout({ children }: PropsWithChildren) {
  return <div className="app-shell"><header><Link to="/restaurants/1/join" className="brand">Mesa <span>24/7</span></Link></header><main>{children}</main></div>
}
