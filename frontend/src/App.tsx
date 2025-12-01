import { Link, Outlet } from "react-router-dom";
import "./App.css";

function App() {
  return (
    <div className="app">
      <div className="background-aurora" />
      <div className="app-shell">
        <header className="app-header">
          <Link to="/" className="logo">
            <span className="logo-mark">🎮</span> Game Price Lens
          </Link>
          <p className="subtitle">Track PC game deals and history</p>
        </header>
        <main className="app-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default App;
