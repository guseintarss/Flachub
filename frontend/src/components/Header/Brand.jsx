import { Link } from 'react-router-dom'
import BrandMark from '../BrandMark'

const Brand = () => {
  return (
    <Link className="brand" to="/" aria-label="ФлакХаб — на главную">
      <BrandMark />
      <span className="brand-text">ФлакХаб</span>
    </Link>
  )
}

export default Brand
