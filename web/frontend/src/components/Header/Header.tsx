import './Header.css';

export default function Header() {
  return (
    <header className="app-header">
      <img 
        src="/assets/logo/sagasu-2.png" 
        alt="Sagasu 2 Logo" 
        className="logo"
      />
      <h1 className="title">SMU Room Availability</h1>
    </header>
  );
}