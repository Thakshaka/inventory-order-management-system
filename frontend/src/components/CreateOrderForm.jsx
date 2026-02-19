import React, { useState, useEffect } from 'react';
import { createOrder, getProducts } from '../api';

const CreateOrderForm = ({ onOrderCreated }) => {
  const [products, setProducts] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await getProducts();
        setProducts(data.items);
        if (data.items.length > 0) {
          setSelectedProductId(data.items[0].id);
        }
      } catch (err) {
        console.error('Failed to load products', err);
      }
    };
    fetchProducts();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!selectedProductId) {
      setError('Please select a product');
      return;
    }
    setSubmitting(true);
    try {
      await createOrder({
        items: [
          {
            product_id: parseInt(selectedProductId),
            quantity: parseInt(quantity),
          },
        ],
      });
      onOrderCreated();
      setQuantity(1);
    } catch (err) {
      setError('Failed to create order. Check stock availability.');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <div className="form-group">
        <label>Product</label>
        <select
          value={selectedProductId}
          onChange={(e) => setSelectedProductId(e.target.value)}
          required
        >
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} — Stock: {p.stock_quantity}
            </option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label>Quantity</label>
        <input
          type="number"
          min="1"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          required
        />
      </div>
      <button type="submit" className="btn-primary" disabled={submitting}>
        {submitting ? 'Creating…' : 'Create Order'}
      </button>
    </form>
  );
};

export default CreateOrderForm;
