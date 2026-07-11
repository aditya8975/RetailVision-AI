import { NavLink } from 'react-router-dom'

export default function Navbar() {
  const linkClass = ({ isActive }) => 'nav-link' + (isActive ? ' active' : '')
  return (
    <div className="navbar">
      <NavLink to="/" className="brand">
        <span className="brand-mark" />
        Lattice
      </NavLink>
      <nav className="nav-links">
        <NavLink to="/" end className={linkClass}>Upload</NavLink>
        <NavLink to="/catalog" className={linkClass}>Catalog</NavLink>
        <NavLink to="/search" className={linkClass}>Visual Search</NavLink>
        <NavLink to="/dashboard" className={linkClass}>Dashboard</NavLink>
      </nav>
    </div>
  )
}
