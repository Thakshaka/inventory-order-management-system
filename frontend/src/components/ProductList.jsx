import React, { useEffect, useState } from 'react';
import { getProducts } from '../api';
import AddProductForm from './AddProductForm';
import Modal from './Modal';

const ProductList = ({ refreshToken }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getProducts();
      setProducts(data.items);
    } catch (err) {
      setError('Failed to fetch products');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [refreshToken]);

  const handleProductAdded = () => {
    setShowModal(false);
    fetchProducts();
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Product Inventory</h2>
        <button className="btn-primary btn-sm" onClick={() => setShowModal(true)}>
          + Add Product
        </button>
      </div>

      {loading && <div className="loading">Loading products…</div>}
      {error && <div className="error">{error}</div>}

      {!loading && !error && (
        <table className="inventory-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Price</th>
              <th>Stock</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>{product.id}</td>
                <td>{product.name}</td>
                <td>${product.price}</td>
                <td>
                  <span className={product.stock_quantity === 0 ? 'stock-empty' : ''}>
                    {product.stock_quantity}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Add New Product"
      >
        <AddProductForm onProductAdded={handleProductAdded} />
      </Modal>
    </div>
  );
};

export default ProductList;
