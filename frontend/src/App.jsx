import { useAuth } from './auth/AuthContext.jsx';
import LoginPage from './components/LoginPage.jsx';
import ChatPage from './components/ChatPage.jsx';

export default function App() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <ChatPage /> : <LoginPage />;
}
