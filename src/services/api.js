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

export const gwasDatasetAnalysis = async (variantString) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/gwas/dataset-analysis`, {
      variant: variantString,
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Dataset analysis failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const getDiseaseAssociations = async (variantString) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/disease-associations`, {
      variant: variantString,
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Disease association lookup failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const getDatasetsSummary = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/datasets/summary`);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to get datasets summary.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable.');
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

export const getCompoundsByGene = async (geneSymbol, limit = 20) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/compounds/by-gene/${encodeURIComponent(geneSymbol)}`, {
      params: { limit },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Gene-targeted compound lookup failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const getDiseasesByRsid = async (rsid) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/rsid-to-disease/${rsid}`);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'RSID disease lookup failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const getDiseasesByRsidsBatch = async (rsids) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/rsid-to-disease/batch`, rsids);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Batch RSID disease lookup failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const getComprehensiveDisease = async (variantString) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/disease-comprehensive/${encodeURIComponent(variantString)}`
    );
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Comprehensive disease lookup failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const generatePatientReport = async (patientReportPayload) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/patient-report`, patientReportPayload);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Patient report generation failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const assemblePatientReport = async (assemblePayload) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/patient-report/assemble`, assemblePayload);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Patient report assembly failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};

export const downloadPatientReportPdf = async (patientReportJson) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/patient-report/pdf`, patientReportJson, {
      responseType: 'blob',
    });
    const disposition = String(response.headers['content-disposition'] || '');
    const match = disposition.match(/filename="?([^";]+)"?/i);
    const filename = match ? match[1] : 'GenVarX_Patient_Report.pdf';
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'PDF download failed.');
    } else if (error.request) {
      throw new Error('Backend server is unreachable. Ensure FastAPI is running on port 8000.');
    } else {
      throw new Error('An unexpected error occurred.');
    }
  }
};
