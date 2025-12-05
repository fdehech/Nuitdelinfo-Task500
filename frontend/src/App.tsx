import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from '@/components/login'
import ProtectedRoute from '@/components/protected-route'
import AdminProtectedRoute from '@/components/admin-protected-route'

function App() {
  console.log("APP VERSION CHECK: ROUTER LOADED")
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<ProtectedRoute />} />
        <Route path="/admin" element={<AdminProtectedRoute />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
