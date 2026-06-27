import Newsletter_button from "./newsletter/Newsletter_button"
import Newsletter_input from "./newsletter/Newsletter_input"

const Newsletter = () => {
    return (
        <div className="footer-newsletter">
            <p><i className="fas fa-bell"></i> Рассылка</p>
            <form className="newsletter-form" onSubmit={(e) => { e.preventDefault(); alert('Спасибо за подписку!'); }}>
                <Newsletter_input />
                <Newsletter_button />
            </form>
        </div>
    )
}

export default Newsletter