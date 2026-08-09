import { useAuth } from './auth/AuthContext.jsx';
import LoginPage from './components/LoginPage.jsx';
import AppShell from './components/AppShell.jsx';

export default function App() {
  const { isAuthenticated } = useAuth();
  // AppShell owns the tab bar and picks which page to show for the role.
  return isAuthenticated ? <AppShell /> : <LoginPage />;
}
