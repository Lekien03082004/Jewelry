import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import logo from '../assets/logo.png'


const Navbar = () => {
    return (
        <>
            <nav className="bg-white shadow-md">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div>
                        <img className="w-20 h-20" src={logo} alt="Logo" />
                    </div>
                    <ul className="flex space-x-8">
                        <li><a href="/">Home</a></li>
                        <li><a href="/products">Products</a></li>
                        <li><a href="/about">About</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                    <div>
                        <input type="text" className="border border-gray-300 rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Search..." />
                        <a href="#">
                            <ShoppingCartIcon />
                        </a>
                        <a href="#">Sign In</a>
                        <a href="#">Sign Up</a>
                        <a href="#">Log Out</a>
                    </div>
                </div>
            </nav>
        </>
    )
}

export default Navbar;