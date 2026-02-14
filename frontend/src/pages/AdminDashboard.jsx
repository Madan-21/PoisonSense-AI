import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../styles/AdminDashboard.css';

const AdminDashboard = () => {
  const [pendingUsers, setPendingUsers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [blogSubmissions, setBlogSubmissions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending'); // 'pending', 'all', or 'blogs'
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        navigate('/login');
        return;
      }

      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      // Fetch all data in parallel
      const [pendingRes, allUsersRes, statsRes, blogsRes] = await Promise.all([
        axios.get('/admin/users/pending', config),
        axios.get('/admin/users/all', config),
        axios.get('/admin/stats', config),
        axios.get('/blog/submissions', config)
      ]);

      setPendingUsers(pendingRes.data.users || []);
      setAllUsers(allUsersRes.data.users || []);
      setStats(statsRes.data);
      setBlogSubmissions(blogsRes.data || []);
      setError('');
    } catch (err) {
      console.error('Error fetching admin data:', err);
      if (err.response?.status === 403) {
        setError('Admin privileges required');
        setTimeout(() => navigate('/'), 2000);
      } else if (err.response?.status === 401) {
        setError('Session expired. Please login again.');
        setTimeout(() => navigate('/login'), 2000);
      } else {
        setError('Failed to load data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (userId, userEmail) => {
    if (!window.confirm(`Approve user ${userEmail}?`)) return;

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `/admin/users/${userId}/approve`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSuccessMessage(`User ${userEmail} approved successfully!`);
      setTimeout(() => setSuccessMessage(''), 3000);
      
      // Refresh data
      fetchData();
    } catch (err) {
      console.error('Error approving user:', err);
      setError(err.response?.data?.detail || 'Failed to approve user');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleReject = async (userId, userEmail) => {
    if (!window.confirm(`Reject and delete user ${userEmail}? This action cannot be undone.`)) return;

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `/admin/users/${userId}/reject`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSuccessMessage(`User ${userEmail} rejected and deleted successfully!`);
      setTimeout(() => setSuccessMessage(''), 3000);
      
      // Refresh data
      fetchData();
    } catch (err) {
      console.error('Error rejecting user:', err);
      setError(err.response?.data?.detail || 'Failed to reject user');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleApproveBlog = async (blogId, blogTitle) => {
    const comment = window.prompt(`Approve blog "${blogTitle}"?\n\nOptional comment (or leave blank):`);
    if (comment === null) return; // User cancelled

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `/blog/submissions/${blogId}/approve`,
        { comment: comment || null },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSuccessMessage(`Blog "${blogTitle}" approved successfully!`);
      setTimeout(() => setSuccessMessage(''), 3000);
      
      // Refresh data
      fetchData();
    } catch (err) {
      console.error('Error approving blog:', err);
      setError(err.response?.data?.detail || 'Failed to approve blog');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleRejectBlog = async (blogId, blogTitle) => {
    const comment = window.prompt(`Reject blog "${blogTitle}"?\n\nPlease provide a reason:`);
    if (!comment || comment === null) {
      alert('A rejection reason is required.');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `/blog/submissions/${blogId}/reject`,
        { comment },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSuccessMessage(`Blog "${blogTitle}" rejected successfully!`);
      setTimeout(() => setSuccessMessage(''), 3000);
      
      // Refresh data
      fetchData();
    } catch (err) {
      console.error('Error rejecting blog:', err);
      setError(err.response?.data?.detail || 'Failed to reject blog');
      setTimeout(() => setError(''), 3000);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRoleBadgeClass = (role) => {
    const roleMap = {
      'admin': 'role-admin',
      'doctor': 'role-doctor',
      'hospital_admin': 'role-hospital',
      'blog_reviewer': 'role-reviewer',
      'poison_center_admin': 'role-center',
      'patient': 'role-patient'
    };
    return roleMap[role] || 'role-default';
  };

  const getBlogStatusBadgeClass = (status) => {
    const statusMap = {
      'pending': 'pending',
      'approved': 'approved',
      'rejected': 'rejected'
    };
    return statusMap[status] || 'pending';
  };

  const getPendingBlogsCount = () => {
    return blogSubmissions.filter(blog => blog.status === 'pending').length;
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="admin-dashboard">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading admin dashboard...</p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="admin-dashboard">
      <div className="admin-header">
        <h1 style={{ 
          color: '#fff !important', 
          textShadow: '0 0 20px rgba(255, 255, 255, 0.8), 2px 2px 8px rgba(0, 0, 0, 0.8)',
          WebkitTextFillColor: '#ffffff',
          filter: 'drop-shadow(2px 2px 4px rgba(0,0,0,0.5))'
        }}>
          🛡️ Admin Dashboard
        </h1>
        <p style={{ 
          color: '#fff !important', 
          textShadow: '0 0 10px rgba(255, 255, 255, 0.6), 1px 1px 4px rgba(0, 0, 0, 0.6)',
          WebkitTextFillColor: '#ffffff'
        }}>
          Manage user approvals and system overview
        </p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span> {error}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          <span>✅</span> {successMessage}
        </div>
      )}

      {/* Statistics Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <h3>{stats.total_users}</h3>
              <p>Total Users</p>
            </div>
          </div>

          <div className="stat-card pending">
            <div className="stat-icon">⏳</div>
            <div className="stat-content">
              <h3>{stats.pending_approvals}</h3>
              <p>Pending Approvals</p>
            </div>
          </div>

          <div className="stat-card approved">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <h3>{stats.approved_users}</h3>
              <p>Approved Users</p>
            </div>
          </div>

          <div className="stat-card verified">
            <div className="stat-icon">📧</div>
            <div className="stat-content">
              <h3>{stats.verified_users}</h3>
              <p>Email Verified</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'pending' ? 'active' : ''}`}
          onClick={() => setActiveTab('pending')}
        >
          ⏳ Pending Approvals ({pendingUsers.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          👥 All Users ({allUsers.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'blogs' ? 'active' : ''}`}
          onClick={() => setActiveTab('blogs')}
        >
          📝 Blog Submissions ({blogSubmissions.length}) 
          {getPendingBlogsCount() > 0 && (
            <span className="badge-count">{getPendingBlogsCount()}</span>
          )}
        </button>
      </div>

      {/* Pending Users Table */}
      {activeTab === 'pending' && (
        <div className="users-section">
          <h2>Pending User Approvals</h2>
          {pendingUsers.length === 0 ? (
            <div className="empty-state">
              <p>🎉 No pending approvals! All caught up.</p>
            </div>
          ) : (
            <div className="users-table-container">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Full Name</th>
                    <th>Role</th>
                    <th>Registration No.</th>
                    <th>Details</th>
                    <th>License</th>
                    <th>Phone</th>
                    <th>Registered</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingUsers.map((user) => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td className="email-cell">{user.email}</td>
                      <td>{user.full_name}</td>
                      <td>
                        <span className={`role-badge ${getRoleBadgeClass(user.role)}`}>
                          {user.role}
                        </span>
                      </td>
                      <td>{user.registration_number || <span style={{color:'#999'}}>N/A</span>}</td>
                      <td>
                        {user.specialization || <span style={{color:'#999'}}>N/A</span>}
                        {user.experience_years && (
                          <div style={{fontSize: '12px', color: '#666'}}>
                            {user.experience_years} yrs exp.
                          </div>
                        )}
                        {user.hospital_address && (
                          <div style={{fontSize: '12px', color: '#666'}}>
                            📍 {user.hospital_address}
                          </div>
                        )}
                      </td>
                      <td>
                        {user.license_document ? (
                          <a
                            href={`${import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace('/api/v1', '') : 'http://localhost:8000'}/${user.license_document}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '4px 10px',
                              backgroundColor: '#e3f2fd',
                              color: '#1565c0',
                              borderRadius: '6px',
                              fontSize: '12px',
                              fontWeight: '600',
                              textDecoration: 'none',
                              border: '1px solid #90caf9'
                            }}
                          >
                            📄 View License
                          </a>
                        ) : (
                          <span style={{color:'#e65100', fontSize: '12px', fontWeight: '500'}}>
                            ⚠️ Not uploaded
                          </span>
                        )}
                      </td>
                      <td>{user.phone || 'N/A'}</td>
                      <td className="date-cell">{formatDate(user.created_at)}</td>
                      <td>
                        <span className="status-badge pending">
                          ⏳ Pending
                        </span>
                      </td>
                      <td className="actions-cell">
                        <button
                          className="btn-approve"
                          onClick={() => handleApprove(user.id, user.email)}
                          title="Approve user"
                        >
                          ✓ Approve
                        </button>
                        <button
                          className="btn-reject"
                          onClick={() => handleReject(user.id, user.email)}
                          title="Reject and delete user"
                        >
                          ✗ Reject
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* All Users Table */}
      {activeTab === 'all' && (
        <div className="users-section">
          <h2>All Users</h2>
          <div className="users-table-container">
            <table className="users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Email</th>
                  <th>Full Name</th>
                  <th>Role</th>
                  <th>Registration No.</th>
                  <th>Phone</th>
                  <th>Registered</th>
                  <th>Email Status</th>
                  <th>Approval Status</th>
                </tr>
              </thead>
              <tbody>
                {allUsers.map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td className="email-cell">{user.email}</td>
                    <td>{user.full_name}</td>
                    <td>
                      <span className={`role-badge ${getRoleBadgeClass(user.role)}`}>
                        {user.role}
                      </span>
                    </td>
                    <td>{user.registration_number || <span style={{color:'#999'}}>N/A</span>}</td>
                    <td>{user.phone || 'N/A'}</td>
                    <td className="date-cell">{formatDate(user.created_at)}</td>
                    <td>
                      <span className={`status-badge ${user.is_verified ? 'verified' : 'unverified'}`}>
                        {user.is_verified ? '✓ Verified' : '✗ Unverified'}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${user.admin_approved ? 'approved' : 'pending'}`}>
                        {user.admin_approved ? '✓ Approved' : '⏳ Pending'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Blog Submissions Table */}
      {activeTab === 'blogs' && (
        <div className="users-section">
          <h2>Blog Submissions</h2>
          {blogSubmissions.length === 0 ? (
            <div className="empty-state">
              <p>📝 No blog submissions yet.</p>
            </div>
          ) : (
            <div className="users-table-container">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Author</th>
                    <th>Submitted</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {blogSubmissions.map((blog) => (
                    <tr key={blog.id}>
                      <td>{blog.id}</td>
                      <td className="blog-title-cell">
                        <div className="blog-title">{blog.title}</div>
                        <div className="blog-description">{blog.description}</div>
                      </td>
                      <td>
                        <span className="category-badge">{blog.category}</span>
                      </td>
                      <td className="email-cell">{blog.author_name}</td>
                      <td className="date-cell">{formatDate(blog.created_at)}</td>
                      <td>
                        <span className={`status-badge ${getBlogStatusBadgeClass(blog.status)}`}>
                          {blog.status === 'pending' && '⏳ Pending'}
                          {blog.status === 'approved' && '✓ Approved'}
                          {blog.status === 'rejected' && '✗ Rejected'}
                        </span>
                      </td>
                      <td className="actions-cell">
                        {blog.status === 'pending' && (
                          <>
                            <button
                              className="btn-approve"
                              onClick={() => handleApproveBlog(blog.id, blog.title)}
                              title="Approve blog"
                            >
                              ✓ Approve
                            </button>
                            <button
                              className="btn-reject"
                              onClick={() => handleRejectBlog(blog.id, blog.title)}
                              title="Reject blog"
                            >
                              ✗ Reject
                            </button>
                          </>
                        )}
                        {blog.status !== 'pending' && (
                          <span className="no-actions">No actions available</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
    <Footer />
    </>
  );
};

export default AdminDashboard;