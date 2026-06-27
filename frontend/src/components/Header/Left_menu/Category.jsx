import { useState, useEffect } from "react"

const Category = () => {
    const [categories, setCategories] = useState([])

    useEffect(() => {
        fetch("/api/mobile/categories/")
            .then((res) => res.json())
            .then((data) => setCategories(data.results || data))
            .catch(() => {})
    }, [])

    return (
        <li className="menu-category">
            <div className="menu-category-title">
                <i className="fas fa-folder"></i> Категории
            </div>
            {categories.map((cat) => (
                <a key={cat.id} href={`/category/${cat.slug}/`} className="menu_link">
                    <i className="fas fa-angle-right"></i> {cat.name}
                </a>
            ))}
        </li>
    )
}

export default Category