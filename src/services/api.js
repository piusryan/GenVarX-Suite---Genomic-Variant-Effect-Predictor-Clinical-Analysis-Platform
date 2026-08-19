import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const annotateVariant = async (variantString) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/annotate`, {
      variant: variantString,
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Variant annotation failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const fetchGwasAssociations = async (variantString) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/gwas`, {
      variant: variantString,
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'GWAS association lookup failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const searchCompounds = async (query, limit = 20) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/compounds`, {
      params: { query, limit },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Compound search failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const getCompound = async (chemblId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/compounds/${chemblId}`);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Compound lookup failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};
