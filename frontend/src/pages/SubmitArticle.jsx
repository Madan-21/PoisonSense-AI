import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/axios";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { formatErrorMessage } from "../utils/errorHandler";
import "../styles/SubmitArticle.css";

const SubmitArticle = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    title: "",
    category: "",
    email: user?.email || "",
    description: "",
    content: "",
    featuredImage: null,
    additionalFiles: null,
  });
  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState({});
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!user) {
      navigate("/login");
    }
  }, [user, navigate]);

  if (!user) {
    return null;
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setErrors((prev) => ({
          ...prev,
          image: "Image size must be less than 5MB",
        }));
        return;
      }
      if (!["image/png", "image/jpeg"].includes(file.type)) {
        setErrors((prev) => ({
          ...prev,
          image: "Only PNG and JPG files are allowed",
        }));
        return;
      }
      setFormData((prev) => ({ ...prev, featuredImage: file }));
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedImage(event.target?.result);
      };
      reader.readAsDataURL(file);
      setErrors((prev) => ({ ...prev, image: undefined }));
    }
  };

  const handleFilesUpload = (e) => {
    const files = Array.from(e.target.files || []);
    const validFiles = [];
    const newErrors = {};

    files.forEach((file) => {
      if (file.size > 10 * 1024 * 1024) {
        newErrors.files = "Each file must be less than 10MB";
        return;
      }
      if (
        ![
          "application/pdf",
          "application/msword",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ].includes(file.type)
      ) {
        newErrors.files = "Only PDF, DOC, and DOCX files are allowed";
        return;
      }
      validFiles.push(file);
    });

    setFormData((prev) => ({ ...prev, additionalFiles: validFiles }));
    setUploadedFiles(validFiles);
    setErrors((prev) => ({ ...prev, ...newErrors }));
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.title.trim()) newErrors.title = "Title is required";
    else if (formData.title.trim().length < 10) newErrors.title = "Title must be at least 10 characters";
    if (!formData.category) newErrors.category = "Category is required";
    if (!formData.description.trim())
      newErrors.description = "Description is required";
    else if (formData.description.length < 50)
      newErrors.description = "Description must be at least 50 characters";
    else if (formData.description.length > 500)
      newErrors.description = "Description must be 500 characters or less";
    if (!formData.content.trim()) newErrors.content = "Content is required";
    if (formData.content.length < 100)
      newErrors.content = "Content must be at least 100 characters";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form Submit Clicked");
    console.log("Form Data:", formData);
    if (validateForm()) {
      console.log("Validation Passed");
      submitArticleToBackend();
    } else {
      console.log("Validation Failed:", errors);
    }
  };

  const submitArticleToBackend = async () => {
    try {
      // Get checkbox state from DOM since it's not in form state
      const confirmCheckbox = document.getElementById("confirm");
      if (!confirmCheckbox?.checked) {
        setErrors({ submit: "Please confirm the checkbox to continue" });
        return;
      }

      // Prepare form data
      const submissionData = {
        title: formData.title,
        category: formData.category,
        description: formData.description,
        content: formData.content,
        featured_image: uploadedImage || null,
        additional_files: uploadedFiles.map(f => f.name),
        is_original: true
      };

      console.log("Submitting to backend:", submissionData);

      // Submit to backend using axios api instance (handles auth token automatically)
      const response = await api.post("/blog/submissions", submissionData);

      console.log("Backend response:", response.data);
      
      // Show success modal
      setSubmitted(true);
      
      // Redirect after 3 seconds
      setTimeout(() => {
        navigate("/blog");
      }, 3000);
    } catch (error) {
      console.error("Submission error:", error);
      
      if (error.response) {
        // Server responded with an error
        const detail = error.response.data?.detail;
        const errorMsg = formatErrorMessage(
          typeof detail === 'string' ? detail :
          Array.isArray(detail) ? detail.map(e => e.msg || e.message || JSON.stringify(e)).join('; ') :
          detail?.message || "Failed to submit article"
        );
        setErrors({ submit: errorMsg });
      } else if (error.request) {
        // Network error
        setErrors({ 
          submit: "⚠️ Cannot connect to server. Please ensure the backend is running." 
        });
      } else {
        setErrors({ submit: "Error: " + error.message });
      }
    }
  };

  const handleCancel = () => {
    navigate("/blog");
  };

  const removeFile = (index) => {
    const updatedFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(updatedFiles);
    setFormData((prev) => ({ ...prev, additionalFiles: updatedFiles }));
  };

  return (
    <>
      <Navbar />
      <div className="submit-article-container">
        <div className="submit-article-wrapper">
          <div className="submit-header">
            <h1>Share Your Knowledge</h1>
            <p>
              Help the community by sharing your poison safety experience and
              expertise
            </p>
          </div>

          <form onSubmit={handleSubmit} className="submit-form">
            <div className="form-section">
              <h2>Article Details</h2>

              <div className="form-group">
                <label htmlFor="title">Article Title * <small>(10-255 characters)</small></label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  placeholder="Enter a compelling title (minimum 10 characters)"
                  value={formData.title}
                  onChange={handleChange}
                  maxLength={255}
                  className={errors.title ? "error" : ""}
                />
                <span className="char-count">
                  {formData.title.length}/255 characters {formData.title.length > 0 && formData.title.length < 10 ? `(need ${10 - formData.title.length} more)` : ""}
                </span>
                {errors.title && (
                  <span className="error-message">{errors.title}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="category">Category *</label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className={errors.category ? "error" : ""}
                >
                  <option value="">Select a category</option>
                  <option value="Prevention">Prevention</option>
                  <option value="First Aid">First Aid</option>
                  <option value="Case Studies">Case Studies</option>
                  <option value="Research">Research</option>
                  <option value="Safety Tips">Safety Tips</option>
                  <option value="Antidotes">Antidotes</option>
                </select>
                {errors.category && (
                  <span className="error-message">{errors.category}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="description">Short Excerpt * <small>(50-500 characters)</small></label>
                <textarea
                  id="description"
                  name="description"
                  placeholder="Brief summary of your article (50-500 characters)"
                  value={formData.description}
                  onChange={handleChange}
                  maxLength="500"
                  rows="3"
                  className={errors.description ? "error" : ""}
                />
                <span className="char-count">
                  {formData.description.length}/500 characters {formData.description.length < 50 && formData.description.length > 0 ? `(need ${50 - formData.description.length} more)` : ""}
                </span>
                {errors.description && (
                  <span className="error-message">{errors.description}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="content">Article Content *</label>
                <textarea
                  id="content"
                  name="content"
                  placeholder="Write your article content here..."
                  value={formData.content}
                  onChange={handleChange}
                  rows="10"
                  className={errors.content ? "error" : ""}
                />
                {errors.content && (
                  <span className="error-message">{errors.content}</span>
                )}
              </div>
            </div>

            <div className="form-section">
              <h2>Media & Attachments</h2>

              <div className="form-group">
                <label>Featured Image</label>
                <div className="upload-box">
                  {uploadedImage ? (
                    <div className="image-preview">
                      <img src={uploadedImage} alt="Featured" />
                      <button
                        type="button"
                        className="remove-btn"
                        onClick={() => {
                          setUploadedImage(null);
                          setFormData((prev) => ({
                            ...prev,
                            featuredImage: null,
                          }));
                        }}
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <>
                      <div className="upload-icon">🖼️</div>
                      <p className="upload-text">
                        Click to upload or drag and drop
                      </p>
                      <p className="upload-hint">PNG, JPG up to 5MB</p>
                      <label htmlFor="featured-image" className="upload-btn">
                        Choose Image
                      </label>
                      <input
                        type="file"
                        id="featured-image"
                        accept="image/png,image/jpeg"
                        onChange={handleImageUpload}
                        style={{ display: "none" }}
                      />
                    </>
                  )}
                </div>
                {errors.image && (
                  <span className="error-message">{errors.image}</span>
                )}
              </div>

              <div className="form-group">
                <label>Additional Files (Optional)</label>
                <div className="upload-box">
                  {uploadedFiles.length > 0 ? (
                    <div className="files-list">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="file-item">
                          <span className="file-icon">📄</span>
                          <span className="file-name">{file.name}</span>
                          <button
                            type="button"
                            className="remove-file-btn"
                            onClick={() => removeFile(index)}
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                      <label
                        htmlFor="additional-files"
                        className="upload-btn upload-btn-secondary"
                      >
                        Add More Files
                      </label>
                    </div>
                  ) : (
                    <>
                      <div className="upload-icon">📎</div>
                      <p className="upload-text">
                        Upload supporting documents, PDFs, or research papers
                      </p>
                      <p className="upload-hint">
                        PDF, DOC, DOCX up to 10MB each
                      </p>
                      <label
                        htmlFor="additional-files"
                        className="upload-btn upload-btn-secondary"
                      >
                        Choose Files
                      </label>
                    </>
                  )}
                  <input
                    type="file"
                    id="additional-files"
                    accept=".pdf,.doc,.docx"
                    multiple
                    onChange={handleFilesUpload}
                    style={{ display: "none" }}
                  />
                </div>
                {errors.files && (
                  <span className="error-message">{errors.files}</span>
                )}
              </div>
            </div>

            <div className="form-section">
              <div className="form-group checkbox-group">
                <input type="checkbox" id="confirm" required />
                <label htmlFor="confirm" className="checkbox-label">
                  I confirm that this content is original, accurate, and does
                  not violate any copyrights. I understand that submissions are
                  reviewed before publication and may be edited for clarity.
                </label>
              </div>
            </div>

            {errors.submit && (
              <div className="error-message" style={{ marginBottom: "20px", display: "block" }}>
                {errors.submit}
              </div>
            )}

            <div className="form-actions">
              <button type="submit" className="submit-btn">
                🚀 Submit for Review
              </button>
              <button
                type="button"
                className="cancel-btn"
                onClick={handleCancel}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Success Modal Popup */}
      {submitted && (
        <div className="modal-overlay">
          <div className="success-modal">
            <div className="success-modal-icon">✓</div>
            <h2>Submitted for Review!</h2>
            <p className="success-modal-message">
              Thank you for contributing to our community. Your article has been
              successfully submitted and will be reviewed by our team within
              24-48 hours.
            </p>
            <div className="success-details">
              <div className="detail-item">
                <span className="detail-icon">📋</span>
                <div className="detail-text">
                  <p className="detail-label">Article Submitted</p>
                  <p className="detail-value">
                    {formData.title || "Your Article"}
                  </p>
                </div>
              </div>
              <div className="detail-item">
                <span className="detail-icon">⏱️</span>
                <div className="detail-text">
                  <p className="detail-label">Review Time</p>
                  <p className="detail-value">24-48 hours</p>
                </div>
              </div>
            </div>
            <button className="modal-btn" onClick={() => navigate("/blog")}>
              Back to Blog
            </button>
          </div>
        </div>
      )}

      <Footer />
    </>
  );
};

export default SubmitArticle;
