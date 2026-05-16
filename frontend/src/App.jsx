import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './api/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import DietPlannerPage from './pages/DietPlannerPage';
import DietResultsPage from './pages/DietResultsPage';
import BodyFatPage from './pages/BodyFatPage';
import ChatbotPage from './pages/ChatbotPage';
import DashboardPage from './pages/DashboardPage';
import DietHistoryPage from './pages/DietHistoryPage';
import ProfilePage from './pages/ProfilePage';
import TeamPage from './pages/TeamPage';
import ContactPage from './pages/ContactPage';
import DeveloperPage from './pages/DeveloperPage';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="spinner-wrap"><div className="spinner-border"></div></div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Login has its own full-page layout */}
          <Route path="/login" element={<LoginPage />} />
          {/* All other pages share Navbar + Footer */}
          <Route path="*" element={<MainLayout />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

function MainLayout() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/"             element={<HomePage />} />
        <Route path="/home"         element={<HomePage />} />
        <Route path="/dietplanner"  element={<DietPlannerPage />} />
        <Route path="/diet-results" element={<DietResultsPage />} />
        <Route path="/bodymass"     element={<BodyFatPage />} />
        <Route path="/dashboard"    element={<ChatbotPage />} />
        <Route path="/chatbot"      element={<ChatbotPage />} />
        <Route path="/progress"     element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/diet-history" element={<ProtectedRoute><DietHistoryPage /></ProtectedRoute>} />
        <Route path="/profile"      element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        <Route path="/team"         element={<TeamPage />} />
        <Route path="/contact"      element={<ContactPage />} />
        <Route path="/rajdeep"      element={<DeveloperPage name="rajdeep" />} />
        <Route path="/prajwal"      element={<DeveloperPage name="prajwal" />} />
        <Route path="/hrishikesh"   element={<DeveloperPage name="hrishikesh" />} />
        <Route path="/bhumika"      element={<DeveloperPage name="bhumika" />} />
      </Routes>
      <Footer />
    </>
  );
}

export default App;
