import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Blog.css";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function Blog() {
  const navigate = useNavigate();

  // Dummy data (replace with API later)
  const featured = {
    tag: "Prevention",
    badge: "Featured",
    title: "Understanding Common Household Poisons: A Parent's Guide",
    excerpt:
      "Learn about the most common household items that can be dangerous to children and how to prevent accidental poisoning.",
    author: "Dr. Sarah Mitchell",
    date: "March 15, 2024",
    read: "5 min read",
    image:
      "https://images.unsplash.com/photo-1556912167-f556f1f39faa?q=80&w=1400&auto=format&fit=crop",
  };

  const posts = [
    {
      id: 1,
      tag: "Prevention",
      title: "Understanding Common Household Poisons: A Parent's Guide",
      excerpt:
        "Learn about the most common household items that can be dangerous to children and how to prevent accidental poisoning.",
      author: "Dr. Sarah Mitchell",
      read: "5 min read",
      image:
        "https://images.unsplash.com/photo-1556912167-f556f1f39faa?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 2,
      tag: "First Aid",
      title: "First Aid for Chemical Burns: What You Need to Know",
      excerpt:
        "Essential steps to take when someone experiences a chemical burn, including immediate actions and when to seek help.",
      author: "Dr. Michael Chen",
      read: "6 min read",
      image:
        "https://images.unsplash.com/photo-1580281657527-47f249e8f8f9?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 3,
      tag: "Case Studies",
      title: "Case Study: Quick Response Saves Life in Opioid Overdose",
      excerpt:
        "A real-life account of how rapid intervention and naloxone administration prevented a tragic outcome.",
      author: "Dr. Emily Rodriguez",
      read: "7 min read",
      image:
        "https://images.unsplash.com/photo-1603398938378-e54eab446dde?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 4,
      tag: "Research",
      title: "Latest Research: AI in Poison Identification and Treatment",
      excerpt:
        "Exploring how artificial intelligence is revolutionizing poison control centers and improving patient outcomes.",
      author: "Dr. James Patterson",
      read: "8 min read",
      image:
        "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 5,
      tag: "Safety Tips",
      title:
        "Workplace Safety: Preventing Chemical Exposure in Industrial Settings",
      excerpt:
        "Best practices for maintaining a safe work environment and protecting workers from hazardous chemical exposure.",
      author: "Robert Thompson",
      read: "6 min read",
      image:
        "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?q=80&w=1400&auto=format&fit=crop",
    },
    {
      id: 6,
      tag: "Antidotes",
      title:
        "Antidote Availability: Ensuring Access in Emergency Situations",
      excerpt:
        "Understanding which antidotes should be readily available and how systems ensure access during emergencies.",
      author: "Dr. Lisa Anderson",
      read: "7 min read",
      image:
        "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?q=80&w=1400&auto=format&fit=crop",
    },
  ];

  return (
    <>
      <Navbar />

      {/* HERO */}
      <section className="blog-hero">
        <div className="blog-hero-inner">
          <h1>PoisonGuard Blog</h1>
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
        {/* FEATURED */}
        <section className="blog-section">
          <h2 className="section-title">Featured Article</h2>

          <article className="featured-card">
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

        {/* LATEST */}
        <section className="blog-section">
          <h2 className="section-title">Latest Articles</h2>

          <div className="blog-grid">
            {posts.map((p) => (
              <article className="post-card" key={p.id}>
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
