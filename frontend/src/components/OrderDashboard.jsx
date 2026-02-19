import React, { useEffect, useState } from 'react';
import { getOrders, shipOrder } from '../api';
import CreateOrderForm from './CreateOrderForm';
import Modal from './Modal';

const OrderDashboard = ({ refreshToken, onOrderCreated }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const fetchOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getOrders();
      setOrders(data.items);
    } catch (err) {
      setError('Failed to fetch orders');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [refreshToken]);

  const handleShip = async (orderId) => {
    try {
      await shipOrder(orderId);
      fetchOrders();
    } catch (err) {
      alert('Failed to ship order');
      console.error(err);
    }
  };

  const handleOrderCreated = () => {
    setShowModal(false);
    fetchOrders();
    if (onOrderCreated) onOrderCreated(); // also triggers stock refresh in parent
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Order Dashboard</h2>
        <button className="btn-primary btn-sm" onClick={() => setShowModal(true)}>
          + Create Order
        </button>
      </div>

      {loading && <div className="loading">Loading orders…</div>}
      {error && <div className="error">{error}</div>}

      {!loading && !error && (
        <table className="order-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Date</th>
              <th>Status</th>
              <th>Items</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id}>
                <td>{order.id}</td>
                <td>{new Date(order.created_at).toLocaleString()}</td>
                <td>
                  <span className={`status-badge status-${order.status.toLowerCase()}`}>
                    {order.status}
                  </span>
                </td>
                <td>
                  <ul className="items-list">
                    {order.items.map((item) => (
                      <li key={item.id}>
                        Product #{item.product_id} × {item.quantity}
                      </li>
                    ))}
                  </ul>
                </td>
                <td>
                  {order.status === 'Pending' && (
                    <button
                      className="btn-ship"
                      onClick={() => handleShip(order.id)}
                    >
                      Ship
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Create New Order"
      >
        <CreateOrderForm onOrderCreated={handleOrderCreated} />
      </Modal>
    </div>
  );
};

export default OrderDashboard;
