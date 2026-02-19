import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
});

export const getProducts = async () => {
  const response = await api.get('/products');
  return response.data;
};

export const getOrders = async () => {
  const response = await api.get('/orders');
  return response.data;
};

export const shipOrder = async (orderId) => {
  const response = await api.patch(`/orders/${orderId}/status`, {
    status: 'Shipped',
  });
  return response.data;
};


export const createProduct = async (product) => {
  const response = await api.post('/products', product);
  return response.data;
};

export const createOrder = async (order) => {
  const response = await api.post('/orders', order);
  return response.data;
};

export default api;
