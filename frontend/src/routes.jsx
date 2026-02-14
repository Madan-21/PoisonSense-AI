import { Routes, Route, Navigate } from "react-router-dom";
import ScrollToTop from "./components/ScrollToTop";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import AiAssistant from "./pages/AiAssistant";
import FindHelp from "./pages/FindHelp";

import Profile from "./pages/Profile";
import AdminPanel from "./pages/AdminPanel";
import AdminDashboard from "./pages/AdminDashboard";
import BlogReviewerDashboard from "./pages/BlogReviewerDashboard";
import DoctorDashboard from "./pages/DoctorDashboard";
import HospitalDashboard from "./pages/HospitalDashboard";
import HospitalInventory from "./pages/HospitalInventory";
import HospitalUpdateInfo from "./pages/HospitalUpdateInfo";
import HospitalReports from "./pages/HospitalReports";
import DoctorVerification from "./pages/DoctorVerification";
import PoisonCenters from "./pages/PoisonCenters";
import PoisonManagement from "./pages/PoisonManagement";
import Blog from "./pages/Blog";
import BlogDetail from "./pages/BlogDetail";
import SubmitArticle from "./pages/SubmitArticle";

import AboutUs from "./pages/AboutUs";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfService from "./pages/TermsOfService";
import ContactSupport from "./pages/ContactSupport";
import MedicalDisclaimer from "./pages/MedicalDisclaimer";
import NotFound from "./pages/NotFound";

import ProtectedRoute from "./components/ProtectedRoute";

export default function AppRoutes() {

  return (
    <>
      <ScrollToTop />
      <Routes>
        {/* ── Public routes ── */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/register" element={<Signup />} />
        <Route path="/find-help" element={<FindHelp />} />
        <Route path="/poison-centers" element={<PoisonCenters />} />
        <Route path="/poison-management" element={<PoisonManagement />} />
        <Route path="/antidotes" element={<PoisonManagement />} />
        <Route path="/blog" element={<Blog />} />
        <Route path="/blog/:id" element={<BlogDetail />} />

        {/* ── Public info pages ── */}
        <Route path="/about" element={<AboutUs />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
        <Route path="/terms" element={<TermsOfService />} />
        <Route path="/contact" element={<ContactSupport />} />
        <Route path="/disclaimer" element={<MedicalDisclaimer />} />

        {/* ── Protected: any logged-in user ── */}
        <Route
          path="/ai-assistant"
          element={
            <ProtectedRoute>
              <AiAssistant />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route path="/dashboard" element={<Navigate to="/" replace />} />
        <Route
          path="/blog/submit"
          element={
            <ProtectedRoute>
              <SubmitArticle />
            </ProtectedRoute>
          }
        />
        <Route
          path="/submit-article"
          element={
            <ProtectedRoute>
              <SubmitArticle />
            </ProtectedRoute>
          }
        />
        <Route
          path="/doctor-verification"
          element={
            <ProtectedRoute>
              <DoctorVerification />
            </ProtectedRoute>
          }
        />

        {/* ── Protected: Admin only ── */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminPanel />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        {/* ── Protected: Blog reviewer / Admin ── */}
        <Route
          path="/blog-reviewer"
          element={
            <ProtectedRoute allowedRoles={['blog_reviewer', 'admin']}>
              <BlogReviewerDashboard />
            </ProtectedRoute>
          }
        />

        {/* ── Protected: Doctor only ── */}
        <Route
          path="/doctor/dashboard"
          element={
            <ProtectedRoute allowedRoles={['doctor', 'admin']}>
              <DoctorDashboard />
            </ProtectedRoute>
          }
        />

        {/* ── Protected: Hospital admin only ── */}
        <Route
          path="/hospital/dashboard"
          element={
            <ProtectedRoute allowedRoles={['hospital_admin', 'admin']}>
              <HospitalDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/hospital/inventory"
          element={
            <ProtectedRoute allowedRoles={['hospital_admin', 'admin']}>
              <HospitalInventory />
            </ProtectedRoute>
          }
        />
        <Route
          path="/hospital/update-info"
          element={
            <ProtectedRoute allowedRoles={['hospital_admin', 'admin']}>
              <HospitalUpdateInfo />
            </ProtectedRoute>
          }
        />
        <Route
          path="/hospital/reports"
          element={
            <ProtectedRoute allowedRoles={['hospital_admin', 'admin']}>
              <HospitalReports />
            </ProtectedRoute>
          }
        />

        {/* ── 404 catch-all ── */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
}
