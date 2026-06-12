import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const getAlerts = async () => {
    try {
        const response = await axios.get(`${API_BASE}/alerts`);
        return response.data;
    } catch (error) {
        console.error('Error fetching alerts:', error);
        return [];
    }
};

export const getStats = async () => {
    try {
        const response = await axios.get(`${API_BASE}/stats`);
        return response.data;
    } catch (error) {
        console.error('Error fetching stats:', error);
        return { total_flows: 0, attacks: 0, normal: 0 };
    }
};

export const getFlows = async () => {
    try {
        const response = await axios.get(`${API_BASE}/flows`);
        return response.data;
    } catch (error) {
        console.error('Error fetching flows:', error);
        return [];
    }
};

export const clearData = async () => {
    try {
        const response = await axios.post(`${API_BASE}/clear`);
        return response.data;
    } catch (error) {
        console.error('Error clearing data:', error);
        return null;
    }
};
