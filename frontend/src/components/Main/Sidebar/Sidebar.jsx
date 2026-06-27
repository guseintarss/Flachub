const Sidebar = (props) => {
    return (
        <div className="modern-sidebar">
            <div className="sidebar-widget">
                <h4 className="widget-title">
                    <i className="fas fa-clock"></i> Свежие статьи
                </h4>
                <div className="recent-posts">
                        <a href="{% url 'post' post.slug %}" className="text-decoration-none recent-post-card">
                            {/* {% if post.photo %} */}
                            <div className="recent-post-img">
                                <img src="{{ post.photo.url }}" alt="{{ post.title }}">
                            </div>
                            {/* {% endif %} */}
                            <div className="recent-post-content">
                                <h5 className="recent-post-title">{{ post.title|truncatechars:50 }}</h5>
                                <div className="recent-post-meta">
                                    <span className="post-author">
                                        <i className="fas fa-user"></i> {{ post.author.username|default:'Аноним' }}
                                    </span>
                                    <span className="post-time" title="{{ post.time_create|date:'d.m.Y H:i' }}">
                                        <i className="fas fa-clock"></i> {{ post.time_create|time_ago }}
                                    </span>
                                </div>
                                <div className="recent-post-stats">
                                    <span className="stat" title="Просмотры">
                                        <i className="fas fa-eye"></i> {{ post.views }}
                                    </span>
                                    <span className="stat" title="Лайки">
                                        <i className="fas fa-heart"></i> {{ post.likes_count|default:post.number_of_likes }}
                                    </span>
                                </div>
                            </div>
                        </a>
                    {/* {% empty %} */}
                        <p className="no-posts">Статей пока нет</p>
                    {/* {% endfor %} */}
                </div>
                <a href="{% url 'home' %}" className="text-decoration-none view-all-link">
                    Смотреть все статьи <i className="fas fa-arrow-right"></i>
                </a>
            </div>

            {/* {% include 'main/list_tags.html' %} */}


            <div className="sidebar-widget categories-widget">
                <h4 className="widget-title">
                    <i className="fas fa-folder"></i> Категории
                </h4>
                <div className="category-list">
                    {/* {% for cat in sidebar_categories|default:"" %} */}
                        <a href="{{ cat.get_absolute_url }}" className="text-decoration-none category-item">
                            <span className="category-name">{{ cat.name }}</span>
                            <span className="category-count">{{ cat.posts_count|default:0 }}</span>
                        </a>
                    {/* {% endfor %} */}
                </div>
            </div>

            <div className="sidebar-widget stats-widget">
                <h4 className="widget-title">
                    <i className="fas fa-chart-bar"></i> Статистика
                </h4>
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-value">{{ total_posts|default:0 }}</div>
                        <div className="stat-label">Статей</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{{ total_users|default:0 }}</div>
                        <div className="stat-label">Авторов</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{{ total_comments|default:0 }}</div>
                        <div className="stat-label">Комментариев</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Sidebar