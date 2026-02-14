import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import "../styles/Blog.css";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function Blog() {
  const navigate = useNavigate();
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        const response = await api.get("/blog/articles");
        setArticles(response.data || []);
      } catch (err) {
        console.error("Error fetching articles:", err);
        setError("Failed to load articles");
      } finally {
        setLoading(false);
      }
    };
    fetchArticles();
  }, []);

  const featured = articles.length > 0 ? {
    id: articles[0].id,
    tag: articles[0].category,
    badge: "Featured",
    title: articles[0].title,
    excerpt: articles[0].description,
    author: articles[0].author_name,
    date: articles[0].published_at ? new Date(articles[0].published_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) : "",
    read: articles[0].read_time || "5 min read",
    image: articles[0].featured_image || "https://images.unsplash.com/photo-1556912167-f556f1f39faa?q=80&w=1400&auto=format&fit=crop",
  } : null;

  const posts = articles.slice(1).map((a) => ({
    id: a.id,
    tag: a.category,
    title: a.title,
    excerpt: a.description,
    author: a.author_name,
    read: a.read_time || "5 min read",
    image: a.featured_image || "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?q=80&w=1400&auto=format&fit=crop",
  }));

  return (
    <>
      <Navbar />

      {/* HERO */}
      <section className="blog-hero">
        <div className="blog-hero-inner">
          <h1>PoisonSense Blog</h1>
          <p>
            Expert insights, safety tips, and the latest research in poison
            prevention and emergency care
          </p>

          <button
            type="button"
            className="btn-ghost"
            onClick={() => navigate("/submit-article")}
          >
            ✍️ Add Your Blog
          </button>
        </div>
      </section>

      <main className="blog-page">
        {loading ? (
          <div style={{ textAlign: "center", padding: "60px 20px" }}>
            <p>Loading articles...</p>
          </div>
        ) : error ? (
          <div style={{ textAlign: "center", padding: "60px 20px" }}>
            <p>{error}</p>
          </div>
        ) : articles.length === 0 ? (
          <div style={{ textAlign: "center", padding: "60px 20px" }}>
            <h2>No Published Articles Yet</h2>
            <p style={{ marginTop: 10, color: "#666" }}>
              Be the first to contribute! Submit your article and it will appear here once approved.
            </p>
          </div>
        ) : (
          <>
        {/* FEATURED */}
        {featured && (
        <section className="blog-section">
          <h2 className="section-title">Featured Article</h2>

          <article className="featured-card" onClick={() => navigate(`/blog/${featured.id}`)} style={{ cursor: "pointer" }}>
            <div
              className="featured-image"
              style={{ backgroundImage: `url(${featured.image})` }}
            />
            <div className="featured-content">
              <div className="badge-row">
                <span className="pill pill-green">{featured.tag}</span>
                <span className="pill pill-yellow">⭐ {featured.badge}</span>
              </div>

              <h3 className="featured-title">{featured.title}</h3>
              <p className="featured-excerpt">{featured.excerpt}</p>

              <div className="meta-row">
                <span>👤 {featured.author}</span>
                <span>📅 {featured.date}</span>
                <span>⏱ {featured.read}</span>
              </div>
            </div>
          </article>
        </section>
        )}

        {/* LATEST */}
        {posts.length > 0 && (
        <section className="blog-section">
          <h2 className="section-title">Latest Articles</h2>

          <div className="blog-grid">
            {posts.map((p) => (
              <article className="post-card" key={p.id} onClick={() => navigate(`/blog/${p.id}`)} style={{ cursor: "pointer" }}>
                <div
                  className="post-image"
                  style={{ backgroundImage: `url(${p.image})` }}
                />
                <div className="post-body">
                  <div className="badge-row">
                    <span className="pill pill-soft">{p.tag}</span>
                  </div>

                  <h3 className="post-title">{p.title}</h3>
                  <p className="post-excerpt">{p.excerpt}</p>

                  <div className="meta-row">
                    <span>👤 {p.author}</span>
                    <span>⏱ {p.read}</span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
        )}
          </>
        )}

        {/* CTA */}
        <section className="blog-cta">
          <h2>Share Your Experience</h2>
          <p>
            Have a poison safety story or prevention tip? Help others by sharing
            your knowledge.
          </p>

          <button
            type="button"
            className="btn-white"
            onClick={() => navigate("/submit-article")}
          >
            ✍️ Add Your Article
          </button>
        </section>
      </main>

      <Footer />
    </>
  );
}
