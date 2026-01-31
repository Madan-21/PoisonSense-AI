import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/BlogDetail.css";

const BlogDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch article from API
  useEffect(() => {
    const fetchArticle = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/v1/blog/articles/${id}`);
        
        if (response.ok) {
          const data = await response.json();
          // Map API fields to component expected fields
          const mappedArticle = {
            ...data,
            author: data.author_name,
            date: new Date(data.published_at).toLocaleDateString('en-US', {
              month: 'long',
              year: 'numeric'
            }),
            readTime: data.read_time || '5 min read',
            image: data.featured_image || '/images/default-article.jpg',
            inlineImage: data.featured_image || '/images/default-article.jpg',
            source: 'PoisonSense AI Community'
          };
          setArticle(mappedArticle);
        } else if (response.status === 404) {
          setError("Article not found");
        } else {
          setError("Failed to load article");
        }
      } catch (err) {
        console.error("Error fetching article:", err);
        setError("Failed to load article");
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [id]);

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="blog-detail-container" style={{textAlign: 'center', padding: '100px 20px'}}>
          <p>Loading article...</p>
        </div>
        <Footer />
      </>
    );
  }

  if (error || !article) {
    return (
      <>
        <Navbar />
        <div className="blog-detail-container">
          <div className="article-not-found">
            <h2>Article Not Found</h2>
            <p>{error || "Sorry, the article you're looking for doesn't exist."}</p>
            <Link to="/blog" className="btn btn-primary">
              Back to Blog
            </Link>
          </div>
        </div>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="blog-detail-container">
        <div className="blog-detail-header">
          <button className="back-button" onClick={() => navigate(-1)}>
            ← Back
          </button>
          <div className="article-badges">
            <span className="badge">{article.category}</span>
            {article.featured && (
              <span className="badge featured-badge">⭐ Featured</span>
            )}
          </div>
        </div>

        <article className="blog-detail-article">
          <div className="article-hero">
            <img src={article.image} alt={article.title} />
          </div>

          <div className="article-content-wrapper">
            <div className="article-meta-header">
              <h1>{article.title}</h1>

              <div className="article-meta-info">
                <div className="author-info">
                  <img
                    src="/images/default-avatar.jpg"
                    alt={article.author}
                    className="author-avatar"
                  />
                  <div className="author-details">
                    <p className="author-name">{article.author}</p>
                    <p className="article-meta-text">
                      {article.date} • {article.readTime}
                    </p>
                  </div>
                </div>
                <p className="article-source">Source: {article.source}</p>
              </div>
            </div>

            <div className="article-body-content">
              {article.inlineImage && (
                <div className="inline-image">
                  <img src={article.inlineImage} alt="Article illustration" />
                </div>
              )}
              {article.content.split("\n").map(
                (paragraph, index) =>
                  paragraph.trim() && (
                    <p
                      key={index}
                      className={
                        paragraph.endsWith(":") ? "section-header" : ""
                      }
                    >
                      {paragraph}
                    </p>
                  ),
              )}
            </div>

            <div className="article-footer">
              <Link to="/blog" className="btn btn-secondary">
                ← Back to Blog
              </Link>
            </div>
          </div>
        </article>
      </div>
      <Footer />
    </>
  );
};

export default BlogDetail;
