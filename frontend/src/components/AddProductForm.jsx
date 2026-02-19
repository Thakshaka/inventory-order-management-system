import React, { useState } from 'react';
import { createProduct } from '../api';

const AddProductForm = ({ onProductAdded }) => {
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [stock, setStock] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createProduct({
        name,
        price: parseFloat(price),
        stock_quantity: parseInt(stock),
      });
      onProductAdded();
      setName('');
      setPrice('');
      setStock('');
    } catch (err) {
      setError('Failed to create product. Please check the values.');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <div className="form-group">
        <label>Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Widget Pro"
          required
        />
      </div>
      <div className="form-group">
        <label>Price ($)</label>
        <input
          type="number"
          step="0.01"
          min="0.01"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          placeholder="e.g. 29.99"
          required
        />
      </div>
      <div className="form-group">
        <label>Stock Quantity</label>
        <input
          type="number"
          min="0"
          value={stock}
          onChange={(e) => setStock(e.target.value)}
          placeholder="e.g. 100"
          required
        />
      </div>
      <button type="submit" className="btn-primary" disabled={submitting}>
        {submitting ? 'Adding…' : 'Add Product'}
      </button>
    </form>
  );
};

export default AddProductForm;
