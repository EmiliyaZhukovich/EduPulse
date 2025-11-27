import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import GroupSelection from './pages/GroupSelection'
import SurveyPage from './pages/SurveyPage'
import CuratorDashboard from './pages/CuratorDashboard'
import AdminDashboard from './pages/AdminDashboard'
import AuthCallback from './pages/AuthCallback'
import Layout from './components/Layout'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/survey" element={<GroupSelection />} />
          <Route path="/survey/:groupId" element={<SurveyPage />} />
          <Route path="/curator" element={<CuratorDashboard />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
