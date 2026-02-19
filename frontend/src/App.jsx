import React, { useState } from 'react';
import ProductList from './components/ProductList';
import OrderDashboard from './components/OrderDashboard';

function App() {
  const [productRefreshToken, setProductRefreshToken] = useState(0);

  // Called by OrderDashboard when an order is created → refresh stock in ProductList
  const handleOrderCreated = () => {
    setProductRefreshToken((prev) => prev + 1);
  };

  return (
    <div className="container">
      <header>
        <h1>Inventory & Order Management</h1>
      </header>
      <main>
        <div className="dashboard-grid">
          <ProductList refreshToken={productRefreshToken} />
          <OrderDashboard onOrderCreated={handleOrderCreated} />
        </div>
      </main>
    </div>
  );
}

export default App;
